#!/usr/bin/python3
"""
Jeff Knerr
Fall 2022

Adds host groups to zabbix server.  

Assumes you have ~/zabbixAuth file, which contains:
URL of your zabbix server (e.g., https://myserver.edu/zabbix)
username
password

Typical uses:
    ./createHostGroup.py -g "My New Group"

"""

from pyzabbix import ZabbixAPI
import argparse
import subprocess
import os, sys
import socket
import click

@click.command()
@click.option('-g','--group', default=None, help="group to add")
def main(group):
    if group==None:
        print("Need a host group to create...")
        sys.exit()
    zabbixAPI = login()
    gid = getGroupID(group, zabbixAPI)
    if gid == None:
        addGroupToZabbix(group, zabbixAPI)
    else:
        print("already have %s group..." % (group))

# ------------------------------------- #

def login():
    """log into Zabbix API as superAdmin, return API object"""
    fn = os.environ["HOME"] + "/zabbixAuth"
    uname,pw,ZURL = readAuth(fn)
    zabbixAPI = ZabbixAPI(ZURL)
    try:
        zabbixAPI.login(uname, pw)
        return zabbixAPI
    except:
        print("Problem with zabbix API login...")
        sys.exit(1)

def readAuth(filename):
    """read in authentication info"""
    try:
        inf = open(filename, "r")
        url = inf.readline().strip()
        uname = inf.readline().strip()
        pw = inf.readline().strip()
        inf.close()
        return uname, pw, url
    except:
        print("Problem reading auth file...")
        sys.exit(1)

def getGroupID(group, zabbixAPI):
    """Search for group by name and try to find id."""
    groupArray = [group]
    groupDictionary = {'name': groupArray}
    ret = zabbixAPI.hostgroup.get(output="extend", filter=groupDictionary)
    if len(ret)==0:
        return None
    else:
        return ret[0]['groupid']

def addGroupToZabbix(group, zabbixAPI):
    """creates a host group in zabbix"""

    print("Creating %s host group in zabbix..." % (group))
    thegroup = {'name':group}
    ret = zabbixAPI.hostgroup.create(thegroup)

    return

def checkIP(oneHost):
    """get host IP address"""
    try:                                 
        ip = socket.gethostbyname(oneHost)
        return ip
    except:
        print("Couldn't find %s's IP..." % (oneHost))
        sys.exit()

# ------------------------------------- #
main()
