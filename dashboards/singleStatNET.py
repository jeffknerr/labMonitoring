#!/usr/bin/python3
"""
Jeff Knerr & Herbie Rand

All Machines: network traffic as single stat
"""                  
from dashboard import *
from panel import *   
from utils import *   
from pyzabbix import ZabbixAPI 
import os                   

postURL = "http://localhost:3000/api/dashboards/db"
base = "https://blade.cs.swarthmore.edu/grafana/"
                          
def main():
    zabAuth = os.environ["HOME"] + "/zabbixAuth"
    grafAuth = os.environ["HOME"] + "/grafanaToken"
    zabbixAPI, token, URL = getCredentials(zabAuth, grafAuth)
    hosts = getHosts(zabbixAPI)
    DB = DashBoard(title="All Machines: net traffic", token=token, panelsPerRow=16, panelHeight = 4)
    panels = []
    for host in hosts:
        q1 = Query(host, "Interface eth0: Bits received", alias="inTraffic")
        q2= Query(host, "Interface eth0: Bits sent", alias="outTraffic")
        link = base + host
        p = SingleStatPanel(title=host, 
                queryArray=[q1,q2], 
                decimals=1, 
                units="bps", 
                orientation="horizontal", 
                textMode="value", 
                colorMode="background", 
                thresholds=[250000,500000,750000,1000000,1250000,1500000], 
                colors=["purple","blue","green","yellow","orange","red"], 
                absLink=link)
        panels.append(p)
    DB.addPanels(panels)
    DB.push(postURL)
main()
