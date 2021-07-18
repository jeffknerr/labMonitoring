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
base = "https://status.cs.swarthmore.edu/grafana"
                          
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
                    "rgb(200,0,0)",
                    "rgb(200,101,50)",
                    "rgb(230,178,50)",
                    "rgb(255,250,12)",
                    "rgb(127,255,50)",
                    "rgb(40,102,10)",
                    "rgb(6, 64, 1)", 
                    "rgb(1, 14, 1)"], 
                # 10min, 30min, 2hour, 1day, 7day, 14day, 30days
                thresholds = ["null",600,1800,7200,86400,604800,1209600,2592000],
                absLink=link)
        panels.append(p)
    db.addPanels(panels)
    db.push(postURL)

main()
