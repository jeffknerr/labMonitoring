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

Both zabbix and grafana were installed from their respective
repositories. See below for pages to follow.

Follow this page for install and configuration:
[https://www.zabbix.com/download?zabbix=4.2&os_distribution=debian&os_version=9_stretch&db=mysql](https://www.zabbix.com/download?zabbix=4.2&os_distribution=debian&os_version=9_stretch&db=mysql)

Follow this page for frontend install and config:
[https://www.zabbix.com/documentation/4.2/manual/installation/install#installing_frontend](https://www.zabbix.com/documentation/4.2/manual/installation/install#installing_frontend)

- change Admin pw
- add users, superAdmin permissions
- set up media and email to use our mail server

#### additional packages on server

Some additional packages installed on the zabbix server:

- apache2
- bind9-host
- mysql-client
- nmap
- python3-pip
- software-properties-common

Also used `pip3` to install some python packages, which we will use when
we add hosts to zabbix.

    pip3 install pyzabbix
    pip3 install click

pyzabbix: [https://github.com/lukecyca/pyzabbix](https://github.com/lukecyca/pyzabbix)
click: [https://palletsprojects.com/p/click/](https://palletsprojects.com/p/click/)

#### additional configs

In `zabbix_agentd.conf`, if you want to write and run your own commands 
on your lab machines, you may need to _enable remote commands_:

    EnableRemoteCommands=1

You also may need to set the `Server` variables:

    Server=127.0.0.1,1.2.3.4            # change 1.2.3.4 to your zabbix server IP
    ServerActive=127.0.0.1,1.2.3.4

### add certbot/letsencrypt

- make sure firewall allows http and https to zabbix server
- add the certbot packages

    sudo apt-get update
    sudo apt-get install certbot python-certbot-apache -t stretch-backports

- set it up for apache: `sudo certbot --apache`
  * provide FQDN for domain name
  * select 2 (redirect all requests to HTTPS) if you want

- now try using https to get to your zabbix frontend


### zabbix adding hosts and items

We are a small computer science department that has labs of
10-30 computers in the building and around campus. When adding hosts to
zabbix, we wanted to group the hosts/computers by lab/room number, to
better keep track of the status of machines in each lab.  

All information about any one computer (e.g., name, IP address, room
number, etc) is stored in ansible, in that computer's `host_vars` file.
With this data in ansible, we can generate lists of computers in each
lab. For example, a `hosts.256` file contains the names of all computers in room 256.

With these "hosts" files, and using `pyzabbix`, we can add hosts to
zabbix, using Group names relating to each lab. For example, all
computers in our `hosts.256` file would be added to zabbix in the
`Lab_256` group.

In the `utils` directory of this repo we include our `addHosts.py` program to add
hosts to zabbix, given a Group and a Template. You can even include more
than one group and more than one template, if you want.

Here's an example of using `addHosts.py` to add to zabbix all machines 
in the file `hosts.256`, to the `Lab_256` group, using the "Template OS
Linux" template (comes with zabbix, and the zabbix group must already
exist in zabbix):

    ./addHosts.py -f hosts.256 -g Lab_256 -t "Template OS Linux"

For all of our linux lab machines and servers, we use the default
templates that come with zabbix:

- Template OS Linux
- Template App SSH Service
- Template Module ICMP Ping

**We also install the zabbix-agent on all machines we want to monitor**.
So all lab machines run zabbix-agent, and allow the zabbix server to 
monitor them.
Here's the relevant part of our config file for the zabbix agent
on each lab machine:

    $ grep -v ^# /etc/zabbix/zabbix_agentd.conf | sort | uniq
    EnableRemoteCommands=1
    Server=1.2.3.4                # put your zabbix server ip here
    ServerActive=1.2.3.4          # and here

At this point we have zabbix running on a server and gathering data 
from all of our servers and lab machines.

Zabbix can make it's own graphs and dashboards. Below is an overview
dashboard with problems and some host graphs and data. See the grafana
install info below that for another way to make pretty dashboards.

![zabbix dashboard](images/zabbix-dash.png)

## install grafana

## guest access 

## set up monitoring and dashboards
