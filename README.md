# monitoring lab machines and servers with zabbix and grafana

We have around 20 servers, 150 lab machines, 10 printers, and a network
switch. We would like to create *status dashboards* to easily show the
current status of our systems. These dashboards should be accessible by the
sysadmins as well as the students and faculty. Ideally, the dashboards
will help the sysadmins discover and diagnose problems, and help the
students and faculty to better utilize the department resources.

Here are two quick examples of the dashboards we will create:

![cpu graphs](images/cpuloads.png)

The above shows CPU load vs. time for all of our lab machines and
servers. Additionally, clicking in the upper-left corner of any graph
takes you to a more detailed status page for that particular computer
(see below).

![uptimes](images/uptimes.png)

This grafana dashboard uses the 
[Singlestat Math Panel](https://grafana.com/grafana/plugins/blackmirror1-singlestat-math-panel)
to show *uptimes* for all lab machines. Additionally, thresholds are set
to color the panels grey (host down), red (host just came up), yellow (up
for less than a day), or green. These panels also include links to 
more detailed dashboard status pages for each computer, like this:

![host detailed status](images/hoststatus.png)

We will use [zabbix](https://www.zabbix.com/manuals) to gather 
the data from the lab machines and servers, and
[grafana](https://grafana.com/) to turn the gathered data into
useful dashboards.

## install zabbix

### preliminaries

For our install (summer 2019) we used debian stretch on a virtual
machine for the zabbix server, running version 4.2.8 of zabbix.

Here's the Zabbix System Information panel to show about how many things
(hosts, items, etc) we are monitoring:

![zabbix system info](images/zabbixSysInfo.png)

For our virtual machine, we are using qemu-kvm, also running on a debian
stretch machine. The kvm host machine has 64GB of memory and 8 CPU
cores, and runs a few other virtual machines for us.

For the actual zabbix server, our virtual machine has 24GB of memory,
4 virtual CPUs, and 31GB of disk space. The memory is probably way
over-provisioned. We are currently using much less than that (output 
from `top` command):

    KiB Mem : 24694224 total,  8368976 free,   786036 used, 15539212 buff/cache
    KiB Swap:  2097148 total,  2097148 free,        0 used. 23273784 avail Mem

And our disk space currently looks like this:

    Filesystem      Size  Used Avail Use% Mounted on
    /dev/sda1        24G   18G  4.4G  81% /
    /dev/sda6       3.9G  2.2G  1.6G  59% /usr
    /dev/sda5       575M  932K  562M   1% /tmp

Of the 18GB used in `/`, almost all of that is in `/var/lib/mysql` where
the data is stored.

### install details

Relevant packages installed on the zabbix server:

- software-properties-common
- python3-pip
- bind9-host
- mysql-client
- nmap
- apache2
- php-mysql
- zabbix-server-mysql
- zabbix-agent
- zabbix-frontend-php
- grafana

### zabbix configuration details

Note: our zabbix server is called `status`, so you'll see that in the prompts.

Following this page:
[https://www.zabbix.com/download?zabbix=4.2&os_distribution=debian&os_version=9_stretch&db=mysql](https://www.zabbix.com/download?zabbix=4.2&os_distribution=debian&os_version=9_stretch&db=mysql)

#### configure mysql for zabbix

    root@status# mysql -uroot -p
    Enter password: 
    Welcome to the MariaDB monitor.  Commands end with ; or \g.
    Your MariaDB connection id is 2
    Server version: 10.1.38-MariaDB-0+deb9u1 Debian 9.8
    
    Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.
    
    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    
    MariaDB [(none)]> create database zabbix character set utf8 collate utf8_bin;
    Query OK, 1 row affected (0.00 sec)
    
    MariaDB [(none)]> grant all privileges on zabbix.* to zabbix@localhost identified by 'super secret password';
    Query OK, 0 rows affected (0.00 sec)
    
    MariaDB [(none)]> quit;
    Bye
    
    root@status# zcat /usr/share/doc/zabbix-server-mysql*/create.sql.gz | mysql -uzabbix -p zabbix
    Enter password: 
    root@status# 

And here's the final config file:

    root@status#  grep -v ^# /etc/zabbix/zabbix_server.conf | sort | uniq
    
    AlertScriptsPath=/usr/lib/zabbix/alertscripts
    CacheSize=64M
    DBName=zabbix
    DBPassword=super secret password                 # <---- NO QUOTES!!!!
    DBSocket=/var/run/mysqld/mysqld.sock
    DBUser=zabbix
    ExternalScripts=/usr/lib/zabbix/externalscripts
    Fping6Location=/usr/bin/fping6
    FpingLocation=/usr/bin/fping
    LogFile=/var/log/zabbix/zabbix_server.log
    LogFileSize=0
    LogSlowQueries=3000
    PidFile=/var/run/zabbix/zabbix_server.pid
    SNMPTrapperFile=/var/log/snmptrap/snmptrap.log
    SocketDir=/var/run/zabbix
    StatsAllowedIP=127.0.0.1
    Timeout=5

## configure zabbix frontend

[https://www.zabbix.com/documentation/4.2/manual/installation/install#installing_frontend](https://www.zabbix.com/documentation/4.2/manual/installation/install#installing_frontend)

Congratulations! You have successfully installed Zabbix frontend.
Configuration file "/usr/share/zabbix/conf/zabbix.conf.php" created.

- change Admin pw
- add users, superAdmin permissions
- set up media and email via our mail server

    $ ls -l /usr/lib/zabbix/alertscripts
    total 4
    -rwxr-xr-x 1 root root 430 Jul 26 20:42 swattxt

(script to mail something to someone, if there's a problem)

## add certbot/letsencrypt

- make sure firewall allows http, https to zabbix server
- add the certbot packages

    sudo apt-get update
    sudo apt-get install certbot python-certbot-apache -t stretch-backports

- set it up for apache: `sudo certbot --apache`

    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Plugins selected: Authenticator apache, Installer apache
    No names were found in your configuration files. Please enter in your domain
    name(s) (comma and/or space separated)  (Enter 'c' to cancel): status.cs.swarthmore.edu
    Obtaining a new certificate
    Performing the following challenges:
    http-01 challenge for status.cs.swarthmore.edu
    Enabled Apache rewrite module
    Waiting for verification...
    Cleaning up challenges
    Created an SSL vhost at /etc/apache2/sites-available/000-default-le-ssl.conf
    Enabled Apache socache_shmcb module
    Enabled Apache ssl module
    Deploying Certificate to VirtualHost /etc/apache2/sites-available/000-default-le-ssl.conf
    Enabling available site: /etc/apache2/sites-available/000-default-le-ssl.conf
     
    Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access.
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    1: No redirect - Make no further changes to the webserver configuration.
    2: Redirect - Make all requests redirect to secure HTTPS access. 
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
    Enabled Apache rewrite module
    Redirecting vhost in /etc/apache2/sites-enabled/000-default.conf to ssl vhost in /etc/apache2/sites-available/000-default-le-ssl.conf
    
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Congratulations! You have successfully enabled https://status.cs.swarthmore.edu

### zabbix adding hosts and items

## install grafana

## set up monitoring and dashboards
