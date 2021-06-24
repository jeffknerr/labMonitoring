#!/usr/bin/python3
"""
Jeff Knerr & Herbie Rand
All Machines: single stat uptime
"""                  

from utils import *
from dashboard import *
from panel import *   
import os                   

postURL = "http://localhost:3000/api/dashboards/db"
#base = "https://blade.cs.swarthmore.edu/grafana/d/3AcvQxVWk/any-single-machine-status?orgId=1&refresh=1m&var-Group=SwatCSComputers&var-Host="
base = "https://blade.cs.swarthmore.edu/grafana"
                          
def main():
    zabAuth = os.environ["HOME"] + "/zabbixAuth"
    grafAuth = os.environ["HOME"] + "/grafanaToken"
    zabbixAPI, token, URL = getCredentials(zabAuth, grafAuth)
    hosts = getHosts(zabbixAPI)
    db = DashBoard(title="All Machines: uptimes", token=token, panelsPerRow=16, panelHeight = 2)
    panels = []
    for host in hosts:
        q = Query(host, "System uptime", alias="uptime")
        link = base+host
        p = SingleStatPanel(title=host, 
                queryArray=[q], 
                colorMode="background",
                units="s",
                calcs="lastNotNull",
                colors = ["grey",
                    "dark-red",
                    "rgb(240,108,34)", 
                    "rgb(234, 206, 57)", 
                    "rgb(103, 204, 22)", 
                    "rgb(32, 133, 12)", 
                    "rgb(6, 64, 1)"], 
                thresholds = ["null",300,600,3600,604800,172800,604800],
                absLink=link)
        panels.append(p)
    db.addPanels(panels)
    db.push(postURL)

main()
