from grafanalib.core import Dashboard,Graph,Row,TimeSeries,GridPos,Stat,Threshold,Text,Time
from grafanalib.zabbix import ZabbixTarget
from grafanalib._gen import DashboardEncoder
import json
import requests
from utils import *   
import os                   
import socket
from subprocess import getstatusoutput as gso
from glibhelpers import *   

common = readCommonData("/home/username/common.txt")
postURL = common['postURL']
base = common['base']
uid = common['uid']
dstype = common['dstype']
datasrc = {"uid": uid, "type": dstype}
zabAuth = os.environ["HOME"] + "/zabbixAuth"
grafAuth = os.environ["HOME"] + "/grafanaToken"
zabbixAPI, token, URL = getCredentials(zabAuth, grafAuth)
hosts = getHosts(zabbixAPI)

kb = 1000.0
thresholds = [0.0,256*kb,512*kb,1024*kb,2048*kb,4096*kb,8192*kb]
colors = ["#00AA00","#33CC00","#66DD00","#99EE00","#CCFF00","yellow","red"]
netthresh = createThresholds(colors, thresholds)

dbtitle="All Machines: network traffic"
h = 4
w = 1
pperrow = 16
plist = []
datasrc = "Zabbix"
group = DEFAULTGROUP

x = 0
y = 0
count = 0
for host in hosts:
    eth = getEthernet(host)
    title = "%s" % host
    # for ubuntu linux
    netitem1 = 'Interface %s: Bits received' % eth
    netitem2 = 'Interface %s: Bits sent' % eth
    if host == "openbsdcomputer":
        netitem1 = "Network interfaces: Incoming network traffic on %s" % eth
        netitem2 = "Network interfaces: Outgoing network traffic on %s" % eth
    zts = []
    zt = ZabbixTarget(item=netitem1,refId="A",group=group,host=host)
    zts.append(zt)
    zt = ZabbixTarget(item=netitem2,refId="B",group=group,host=host)
    zts.append(zt)
    link = base + host
    linkdict = {"title": "Click to go", "url": link }
    thestat = Stat(
            title="%s " % host,
            dataSource=datasrc, 
            targets=zts,
            thresholds=netthresh,
            reduceCalc="last",
            graphMode="none",
            decimals=1,
            colorMode="background",
            gridPos=GridPos(h=h, w=w, x=x, y=y),
            links=[linkdict]
            )
    plist.append(thestat)
    count += 1
    x += w
    if count%pperrow == 0:
        x = 0
        y = y + h
# ------------------------------------------------------------------- #
timeobj = Time("now-5m", "now")
fresh = "1m"
tz = ""
dashboard = Dashboard(title=dbtitle, panels=plist, timezone=tz, refresh=fresh, tags=["MYtag"], time=timeobj).auto_panel_ids()
api_key = token
server = "localhost:3000"

jsondash = json.dumps(
        {
            "dashboard": dashboard.to_json_data(),
            "overwrite": True,
            "message": "updated by grafanalib"
        }, sort_keys=True, indent=2, cls=DashboardEncoder)


headers = {'Authorization': f"Bearer {api_key}", 'Content-Type': 'application/json'}
r = requests.post(f"http://{server}/api/dashboards/db", data=jsondash, headers=headers, verify=True)
