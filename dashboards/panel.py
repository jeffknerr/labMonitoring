"""
Herbie Rand
Summer 2019

The panel class works with the dashboard class as part of Swat's 
custom grafana API. Panels are the data displays that can be 
created in a dashboard. Currently supported types of panels:
    - GraphPanel
    - SingleStatPanel

https://github.com/hrand1005/grafapyAPI
"""

import json
import sys

colorDictionary = {"red":"#C4162A", "blue":"#1F60C4", "green":"#37872D", "yellow":"#E0B400", 
        "orange":"#FA6400", "purple":"#440563", "baby blue":"#8AB8FF", "grey":"#757575"}

class Panel:
    def __init__(self, panelType, title="title", queryArray=None, JSON=None, absLink=None):
        """
        Parameters: panelType (required), optional title and queryArray. If json found,
                    initializes panel from json data instead of other arguments.
              NOTE: This constructor should not be called directly. Initialize your 
                    panels from one of the supported panel type constructors.
        """
        if JSON!=None:
            print("Initializing panel from json...")
            self.dictionary = json.loads(JSON)
            self.title = self.dictionary["title"]
            self.type = self.dictionary["type"]
            #throw exception if panelType != self.type
            self.queries=[]
            for target in self.dictionary["targets"]:
                host = target["host"]["filter"]
                group = target["group"]["filter"]
                item = target["item"]["filter"]
                application = target["application"]["filter"]
                q = Query(host, item, group=group, application=application)
                self.queries.append(q)
            h = self.dictionary["gridPos"]["h"]
            w = self.dictionary["gridPos"]["w"]
            x = self.dictionary["gridPos"]["x"]
            y = self.dictionary["gridPos"]["y"]
            self.id = 0
            self.position = [x, y]
            self.size = [h, w]
            self.sizeSet = False
        else:
            print("Initializing panel (%s) from arguments..." % title)
            self.title = title
            self.type = panelType
            self.queries = []
            self.dictionary = {}
            self.id = 0
            self.position = [0, 0]
            self.size = [8, 12]
            self.sizeSet = False
            if absLink!=None:
                self.links=[{"title":"Click to go", "type":"absolute", "url":absLink}]
            else:
                self.links=None
            if queryArray!=None:
                self.queries.extend(queryArray)

    def _readJSON(self, filename):
        """read json from file, return as dict"""
        jPanel = open(filename)
        panelStr = jPanel.read()
        jPanel.close()
        d = json.loads(panelStr)
        return d
    
    def getDictionary(self):
        """ Returns: panel's dictionary (python, not json) """
        return self.dictionary

    def getType(self):
        """ Returns: this panel's type """
        return self.type

    def getTitle(self):
        """ Returns: this panel's title """
        return self.title

    def getQueries(self):
        """ Returns: array of this panel's queries """
        return self.queries
    
    def setID(self, panelID):
        """ Parameters: panelID (positive int) """
        self.id = panelID
        if "id" in self.dictionary:
            self.dictionary["id"] = self.id

    def getID(self):
        """ Returns: this panel's id """
        return self.id

    def _setPosition(self, x, y):
        """ Parameters: x and y value to set panel position in dashboard """
        self.position = [x, y]
        self.dictionary["gridPos"]["x"] = x
        self.dictionary["gridPos"]["y"] = y
    
    def getPosition(self):
        """ Returns: list[x,y] of panel position in the dashboard """
        return self.position
    
    def getSize(self):
        """ Returns: this panel's size [h, w] """
        return self.size

    def _setSize(self, h, w):
        """ Parameters: height and width """
        if not(self.sizeSet):
            self.size = [h, w]
            self.dictionary["gridPos"]["h"] = h
            self.dictionary["gridPos"]["w"] = w
            self.sizeSet = True
        else:
            print("The size on this panel has already been set.")
            print("Height: %s, Width: %s" % (self.size[0], self.size[1]))

    def _sizeSet(self):
        """ Returns: bool indicating whether the size has been set on this panel.  """
        return self.sizeSet

    def containsItem(self, itemName):
        """
        Parameters: name of item
        Returns: bool, true if this panel contains itemName, else false
        """
        for query in self.queries:
            if query.getItem()==itemName:
                return True
        return False

    def containsHost(self, hostName):
        """
        Parameters: name of host
        Returns: bool, true if this panel contains hostName, else false
        """
        for query in self.queries:
            if query.getHost()==hostName:
                return True
        return False
    
    def addQueries(self, queryList):                                              
        """ Parameters: list of query objects to be added to this panel """
        for query in queryList:
            #Throw exceptions when someone gives something that's not a query object
            targetDict = {}
            if query.getApplication()!=None:
                targetDict["application"] = {"filter": query.getApplication()}
            else:
                targetDict["application"] = {"filter": ""}
            targetDict["functions"] = [{
                "added": False,
                "def": {
                    "category": "Alias",
                    "defaultParams": [],
                    "name": "setAlias",
                    "params": [{
                        "name": "alias",
                        "type": "string"
                        }]
                    },
                "params": [query.getItem()],
                "text": "setAlias(" + query.getItem() + ")"
                }]
            if query.getAlias()!=None:
                targetDict["functions"][0]["params"] = [query.getAlias()]
                targetDict["functions"][0]["text"] = "setAlias(" + query.getAlias() + ")"
            targetDict["group"] = {"filter": query.getGroup()}
            targetDict["host"] = {"filter": query.getHost()}
            targetDict["item"] = {"filter": query.getItem()}
            targetDict["mode"] = 0
            targetDict["options"] = {"showDisabledItems": False, "skipEmptyValues": False}
            targetDict["refId"] = "A"
            targetDict["resultFormat"] = "time_series"
            targetDict["table"] = {"skipEmptyValues": False}
            if query.getMode()!=None:
                targetDict["mode"] = query.getMode()
            self.dictionary["targets"].append(targetDict)

class SingleStatPanel(Panel):

    def __init__(self, title="title", queryArray=None, valueMaps=None, rangeMaps=None, 
            prefix=None, postfix=None, colors=None, thresholds=None, units=None, JSON=None, 
            decimals=None, colorMode=None, graphMode=None, absLink=None, calcs=None):

        Panel.__init__(self, "singlestat", title=title, queryArray=queryArray, JSON=JSON, absLink=absLink)
        if JSON==None:
            self._buildDictionary(valueMaps, rangeMaps, prefix, postfix, colors, 
                    thresholds, units, decimals, colorMode, graphMode, calcs)

    def _buildDictionary(self, valueMaps, rangeMaps, prefix, postfix, colors, thresholds, 
            units, decimals, colorMode, graphMode, calcs):
        """called by constructor, builds singlestat panel dictionary"""
        singleStatDictionary = self._readJSON("singlestat.json")
        singleStatDictionary["title"] = self.title
        if self.links!=None:
            singleStatDictionary["links"] = self.links
        if units!=None:
            singleStatDictionary["fieldConfig"]["defaults"]["unit"]=units
        if decimals!=None:
            singleStatDictionary["fieldConfig"]["defaults"]["decimals"]=decimals
        if thresholds!=None:
            steps = []
            for i in range(len(thresholds)):
                color = colors[i]
                thresh = thresholds[i]
                d = {"color":color, "value":thresh}
                steps.append(d)
            singleStatDictionary["fieldConfig"]["defaults"]["thresholds"]["steps"] = steps
        if calcs != None:
            singleStatDictionary["options"]["reduceOptions"]["calcs"] = [calcs]
        if colorMode != None:
            singleStatDictionary["options"]["colorMode"] = colorMode
        else:
            singleStatDictionary["options"]["colorMode"] = "value"
        if graphMode != None:
            singleStatDictionary["options"]["graphMode"] = "area"
        else:
            singleStatDictionary["options"]["graphMode"] = "none"
        self.dictionary = singleStatDictionary             
        if self.queries!=None:                        
            self.addQueries(self.queries)
        self.id = 0
        self.position = [0,0]
    
    def addValueMap(self, valueMaps):
        """
        Parameters: an array of dictionaries that makes up a value map
        Description: maps values in the singlestat panel according to given array of dictionaries
        """
        #perform check on the value map to make sure it is of the right type
        self.dictionary["valueMaps"]=valueMaps


class GraphPanel(Panel):

    def __init__(self, title="title", queryArray=None, yAxesLeftMinMax=None, JSON=None, 
            absLink=None, units=None, bars=None):
        """
        Parameters: optional title and queryArray, title is 'title' by default
            queries can be added later with "addQueries()"
            optional yAxesLeftMinMax=[0,800000000] sets hard min/max for all graphs
        """
        Panel.__init__(self, "graph", title=title, queryArray=queryArray, JSON=JSON, absLink=absLink)
        if JSON==None:
            self._buildDictionary(yAxesLeftMinMax, units, bars)

    def _buildDictionary(self, yAxesLeftMinMax, units, bars):
        """
        Description: to be called by constructor, builds graph dictionary
        """

        graphDictionary = self._readJSON("graphpanel.json")
        graphDictionary["title"] = self.title
        if self.links!=None:
            graphDictionary["links"] = self.links
        if bars!=None:
            graphDictionary["bars"] = "true"
        if units != None:
            graphDictionary["yaxes"][0]["format"] = units
            graphDictionary["yaxes"][1]["format"] = units
        if yAxesLeftMinMax != None:
            graphDictionary["yaxes"][0]["min"] = yAxesLeftMinMax[0]
            graphDictionary["yaxes"][0]["max"] = yAxesLeftMinMax[1]
                            
        self.dictionary = graphDictionary
        if self.queries!=None:
            self.addQueries(self.queries)
        self.id = 0
        self.position = [0,0]

class Query:

    def __init__(self, host, item, group="/.*/", application=None, mode=None, alias=None):
        """
        Parameters: host name, item name, group and application name optional (group and application
            are optional filters that can be applied in grafana to help find the correct hosts/items,
            especially if there are duplicate host/item names)
            mode: number corresponding to the type of data displayed in your query. 
                Example: mode=0 (for metric queries)
                         mode=2 (for text queries)
        """
        self.host = host
        self.item = item
        self.group = group
        self.application = application
        self.mode = mode
        self.alias = alias

    def getHost(self):
        """
        Returns: host name for this query
        """
        return self.host
    
    def getItem(self):
        """
        Returns: item name for this query
        """
        return self.item

    def getGroup(self):
        """
        Returns: group name for this query
        """
        return self.group

    def getApplication(self):
        """
        Returns: application name for this query, may return 'None'
        """
        return self.application
    
    def getMode(self):
        """
        Returns: mode for this query's data
        """
        return self.mode
    
    def getAlias(self):
        """
        Returns: alias for this query
        """
        return self.alias
