from grafanalib.core import TimeSeries, GridPos, Stat, Threshold
from grafanalib.zabbix import ZabbixTarget
import socket
from subprocess import getstatusoutput as gso

GYOR = ['green','yellow','orange','red']
ROYG = ['red','orange','yellow','green']
ROYGGGG = ['red','orange','yellow','#66EE66','#44CC44','#22AA22','grey']
GGGGYOR = ['grey', '#22AA22', '#44CC44', '#66EE66', 'yellow', 'orange', 'red']

def createThresholds(colors, values):
    """create a list of threshold objects"""
    if len(colors) != len(values):
        print("not enough colors or values???")
    thresholds = []
    for i in range(len(colors)):
         level = Threshold(colors[i], i, values[i])
         thresholds.append(level)
    return thresholds

def createGraph(host, title, datasrc, group, targets, xcol, yrow, height, width, gmin=0, gmax=100):
    """put all params and targets into a Graph object"""
    gtargets = []
    rid = "A"
    if len(targets) > 26:
        print("that's a lot of targets for one graph!!!")
    for t in targets:
        zt = ZabbixTarget(item=t,refId=rid,group=group,host=host)
        gtargets.append(zt)
        rid = chr(ord(rid) + 1)  # bug if more than 26 targets....
    thegraph = TimeSeries(
            title=title, 
            dataSource=datasrc, 
            targets=gtargets,
            lineWidth=2,
            pointSize=1,
            fillOpacity=8,
            min=gmin,
            max=gmax,
            gridPos=GridPos(h=height, w=width, x=xcol, y=yrow))
    return thegraph

def createStat(host, base, statTitle, datasrc, zt, xcol, yrow, height, width, holds, dcs=0):
    """put all params and targets into a Graph object"""
    link = base + host
    linkdict = {"title": "Click to go", "url": link }
    thestat = Stat(
            title="%s %s" % (host, statTitle),
            dataSource=datasrc, 
            targets=[zt],
            thresholds=holds,
            reduceCalc="lastNotNull",
            graphMode="none",
            decimals=dcs,
            colorMode="background",
            gridPos=GridPos(h=height, w=width, x=xcol, y=yrow),
            links=[linkdict]
            )
    return thestat

def readCommonData(fn):
    """get common data from file, return as dict"""
    common = {}
    inf = open(fn, "r")
    for line in inf:
        key, value = line.strip().split("|")
        common[key] = value
    inf.close()
    return common

def getEthernet(host):
    """try to get primary ethernet name, like eth0, or eno1"""
    ip = socket.gethostbyname(host)
    com = "zabbix_get -s %s -k net.if.discovery" % ip
    status, output = gso(com)
    # examples: 
    #[{"{#IFNAME}":"lo"},{"{#IFNAME}":"eno1"},{"{#IFNAME}":"eno2"},{"{#IFNAME}":"enp2s0f0"},{"{#IFNAME}":"enp2s0f1"}]
    #[{"{#IFNAME}":"lo0"},{"{#IFNAME}":"em0"},{"{#IFNAME}":"em1"},{"{#IFNAME}":"enc0"},{"{#IFNAME}":"pflog0"}]
    #{"data":[{"{#IFNAME}":"lo"},{"{#IFNAME}":"ens3"}]}
    #[{"{#IFNAME}":"lo"},{"{#IFNAME}":"enp2s0"},{"{#IFNAME}":"enp3s0"}]
    #{"data":[{"{#IFNAME}":"enp3s0"},{"{#IFNAME}":"lo"},{"{#IFNAME}":"enp2s0"}]}
    #[{"{#IFNAME}":"lo"},{"{#IFNAME}":"ens3"}]
    if status == 0:
        if "data" in output:
            output = output.strip("{}")
            output = output[7:]
        data = output.strip("][").split(",")
        names = []
        for item in data:
            name = item.strip("{}").split(":")[1]
            names.append(name.strip('"'))
        # do not use the loopback....
        if "lo" in names:
            names.remove("lo")
        if "lo0" in names:
            names.remove("lo0")
        if "docker0" in names:
            names.remove("docker0")
        names.sort()
        eth = names[0]
        #print(host, eth, names)
        return eth
    else:
        print("Problem using zabbix_get to get ethernet interface for %s" % host)
        return "eth0"
