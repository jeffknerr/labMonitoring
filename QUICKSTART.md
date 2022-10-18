
For the impatient...and not done yet...
---

```
$ sudo virsh shutdown blade
$ sudo virsh destroy blade
$ sudo virsh undefine blade

```


```
allspice$ cd /etc/ansible
vim host_vars/blade
vim host_vars/kvmd
vim roles/faiserver/files/disk_config/blade
```

```
allspice$ cd /etc/ansible/bin
sudo ./installVM.sh blade

```

Above should create VM, run playbook to set it up, run 
SSH-after-FAI, reboot it. Then need to log in and reset
sysamin, parrish, and root passwords, update tripwire.

Knerr clone the dotfiles repo, then run makeitso.

Above playbooks installed zabbix 6.2.3 and grafana 9.2.

```
top - 12:10:50 up 5 min,  1 user,  load average: 0.04, 0.05, 0.00
Tasks: 110 total,   1 running, 109 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  3.0 sy,  0.0 ni, 97.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :  64321.0 total,  63851.6 free,    184.4 used,    285.0 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.  63542.9 avail Mem

knerr@blade ~ $ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        53G  1.2G   49G   3% /
/dev/sda4       7.8G  3.2G  4.3G  43% /usr
/dev/sda3       574M   56K  562M   1% /tmp
```

Change the libvirt stuff:

```
ssh kvmhost
sudo virsh shutdown kvmguest
sudo virsh edit kvmguest
    <interface type='bridge'>
      <mac address='52:54:00:00:00:3a'/>
      <source bridge='br0'/>
      <model type='e1000'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
change to 
    <interface type='bridge'>
      <mac address='52:54:00:00:00:3a'/>
      <source bridge='br0'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
sudo virsh start kvmguest
```

```
ssh kvmguest
$ ip a
2: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 52:54:00:00:00:3a brd ff:ff:ff:ff:ff:ff
....
....
$ cat /sys/devices/pci0000:00/0000:00:03.0/virtio0/net/ens3/statistics/rx_bytes
227194
```

Secure the mysql install:

```
$ sudo mysql_secure_installation

Enter current password for root (enter for none):

Switch to unix_socket authentication [Y/n] n

Change the root password? [Y/n] n

Remove anonymous users? [Y/n] y

Disallow root login remotely? [Y/n] y

Remove test database and access to it? [Y/n] y

Reload privilege tables now? [Y/n] y

Thanks for using MariaDB!

```

Now test it and make an admin account:

```
$ sudo mysql
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 36
Server version: 10.5.15-MariaDB-0+deb11u1 Debian 11

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> GRANT ALL ON *.* TO 'admin'@'localhost' IDENTIFIED BY 'useGoodpwHere' WITH GRANT OPTION;
Query OK, 0 rows affected (0.004 sec)

MariaDB [(none)]> flush privileges;
Query OK, 0 rows affected (0.001 sec)

MariaDB [(none)]> exit
Bye


$  sudo systemctl status mariadb
$  sudo mysqladmin version
$  mysqladmin -u admin -p version
```

The last two should show the same info.

Now back to zabbix mysql setup...


```

$ sudo mysql -u root -p
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.

MariaDB [(none)]> create database zabbix character set utf8mb4 collate utf8mb4_bin;
Query OK, 1 row affected (0.001 sec)

MariaDB [(none)]> create user zabbix@localhost identified by 'graphsRc00l';
Query OK, 0 rows affected (0.014 sec)

MariaDB [(none)]> grant all privileges on zabbix.* to zabbix@localhost;
Query OK, 0 rows affected (0.003 sec)

MariaDB [(none)]> set global log_bin_trust_function_creators = 1;
Query OK, 0 rows affected (0.001 sec)

MariaDB [(none)]> quit;
Bye

$ zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix
Enter password:
(takes a minute or two here...)

$ sudo mysql -u root -p
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.

MariaDB [(none)]> set global log_bin_trust_function_creators = 0;
Query OK, 0 rows affected (0.000 sec)

MariaDB [(none)]> exit
Bye

```

Now set up config options for zabbix (only showing options I changed):

```
$ sudo grep -v ^# /etc/zabbix/zabbix_server.conf | sort | uniq
CacheSize=96M
DBPassword=myzabbixmysqlPW
ValueCacheSize=64M
...
...
```

But don't start it yet!!! First set up certbot and the SSL cert:

```
$ sudo certbot --apache
Enter email address (used for urgent renewal and security notices)
 (Enter 'c' to cancel): myusername@college.edu

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.3-September-21-2022.pdf. You must
agree in order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y
Account registered.
No names were found in your configuration files. Please enter in your domain
name(s) (comma and/or space separated)  (Enter 'c' to cancel): blade.cs.swarthmore.edu
Requesting a certificate for blade.cs.swarthmore.edu
Performing the following challenges:
http-01 challenge for blade.cs.swarthmore.edu
Enabled Apache rewrite module
Waiting for verification...
Cleaning up challenges
Created an SSL vhost at /etc/apache2/sites-available/000-default-le-ssl.conf
Enabled Apache socache_shmcb module
Enabled Apache ssl module
Deploying Certificate to VirtualHost /etc/apache2/sites-available/000-default-le-ssl.conf
Enabling available site: /etc/apache2/sites-available/000-default-le-ssl.conf
Enabled Apache rewrite module
Redirecting vhost in /etc/apache2/sites-enabled/000-default.conf to ssl vhost in /etc/apache2/sites-available/000-default-le-ssl.conf

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations! You have successfully enabled https://blade.cs.swarthmore.edu
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
$

```



```
$ sudo a2enmod proxy proxy_http
Enabling module proxy.
Considering dependency proxy for proxy_http:
Module proxy already enabled
Enabling module proxy_http.
To activate the new configuration, you need to run:
  systemctl restart apache2

$ sudo vim /etc/apache2/sites-enabled/000-default-le-ssl.conf
(added/changed these)
        ServerName www.example.com
        ServerAdmin webmaster@www.example.com

        ProxyRequests Off
        ProxyPreserveHost On
        ProxyPass /grafana http://localhost:3000
        ProxyPassReverse /grafana http://localhost:3000

$ sudo systemctl restart apache2.service

```


Configure zabbix frontend:

```
https://blade.cs.swarthmore.edu/zabbix/setup.php
changes made:
 - server name: SwatCS
 - zabbix password: used one from above
 - time zone: america new york
```

Now log in with the defaults (Admin, zabbix) and change them:

- add your own user with group:zabbixAdmin and permission: superAdmin
- log out of Admin account, log in as your own user
- disable Admin, Guest accounts

Now add a few more python goodies:

```
   56  10/12/2022 13:01  sudo apt-get update
   57  10/12/2022 13:01  sudo apt-get upgrade
   58  10/12/2022 13:01  sudo apt-get autoremove
   59  10/12/2022 13:01  sudo pip3 install pyzabbix
   60  10/12/2022 13:01  sudo pip3 install click
   61  10/12/2022 13:02  sudo pip3 install mysql-connector-python
   62  10/12/2022 13:02  sudo pip3 install grafanalib

```

```
   64  10/12/2022 13:05  cd /etc/tripwire
   65  10/12/2022 13:05  ll
   66  10/12/2022 13:05  cat README
   67  10/12/2022 13:06  sudo tripwire --init
   68  10/12/2022 13:06  sudo tripwire --check --interactive
```


Finally...start setting up zabbix
---

Start zabbix:

```
systemctl start zabbix-server
```

Add your own host groups: Config->Host groups->Create host group

```
  105  10/12/2022 13:26  ./createHostGroups.py -g Lab_238
  106  10/12/2022 13:27  ./createHostGroups.py -g Linux servers
  107  10/12/2022 13:27  ./createHostGroups.py -g "Linux servers"
  108  10/12/2022 13:27  ./createHostGroups.py -g "Linux servers2"
  109  10/12/2022 13:27  vim createHostGroups.py
  110  10/12/2022 13:30  ./createHostGroups.py -g Lab_238
  111  10/12/2022 13:30  vim createHostGroups.py
  112  10/12/2022 13:30  ll
  113  10/12/2022 13:30  cat update_zabbix_hosts
  114  10/12/2022 13:30  cp update_zabbix_hosts addgroups
  115  10/12/2022 13:30  vim addgroups
  116  10/12/2022 13:34  ./addgroups
  117  10/12/2022 13:34  pwd
  118  10/12/2022 13:34  ls
  119  10/12/2022 13:34  vim addgroups
  120  10/12/2022 13:34  ./addgroups
```

Add some custom templates:

- Configuration
- Templates
- Import
- select the one you want (cslab, gpu, ldap, etc)

(automate this???)

Add some hosts

```
allspice$ sudo scp /usr/swat/db/hosts.* blade:/usr/swat/db/.
also need peermon and gpu file (solved by running updateMonitoring??)

./add-all
```


Grafana setup
---

```
  180  10/12/2022 15:43  sudo vim /etc/grafana/grafana.ini
  181  10/12/2022 15:45  sudo systemctl restart grafana-server.service
  182  10/12/2022 15:47  sudo grafana-cli plugins install alexanderzobnin-zabbix-app
  183  10/12/2022 15:48  sudo grafana-cli plugins install grafana-clock-panel
  184  10/12/2022 15:48  sudo grafana-cli plugins install grafana-polystat-panel
```

- installed plugins, datasource
- enabled zabbix as data source
- made zabbix user (grafana) with full access
- set up grafan zabbix plugin page (use zabbix grafana user pw)

- add knerr user (w grafana admin, main org admin privs)
- now make dashboards: test dash w/zabbix datasource


- also guest grafana.ini config options (and test)

- make the anysinglemachine variables and dashboard first
  (import a good version of AnySingleMachine, fix stuff)
- then make the api key/token (now make service account)
- now try our programs to auto-make dashboards




















