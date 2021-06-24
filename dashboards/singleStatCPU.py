#!/usr/bin/python3
"""
Jeff Knerr & Herbie Rand

All Machines: cpu single stat
"""                  
from dashboard import *
from panel import *   
from utils import *   
import os                   

postURL = "http://localhost:3000/api/dashboards/db"
base = "https://blade.cs.swarthmore.edu/grafana/"
                          
def main():
    zabAuth = os.environ["HOME"] + "/zabbixAuth"
    grafAuth = os.environ["HOME"] + "/grafanaToken"
    zabbixAPI, token, URL = getCredentials(zabAuth, grafAuth)
    hosts = getHosts(zabbixAPI)
    db = DashBoard(title="All Machines: cpu single stat", token=token, panelsPerRow=16, panelHeight = 2)
    panels = []
    for host in hosts:
        q = Query(host, "Load average (1m avg)", alias="cpuload")
        link = base + host
        p = SingleStatPanel(title=host, 
                queryArray=[q], 
                decimals=1, 
                thresholds = [0,1,2,5,10],
                colors=["grey", "green","yellow","orange","red","white"], 
                colorMode="background", 
                absLink=link)
        panels.append(p)
    db.addPanels(panels)
    db.push(postURL)


main()
