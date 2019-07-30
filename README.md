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

## install grafana

## set up monitoring and dashboards
