#!/usr/bin/env python
"""
Kegg

Common Library

KeggAPI handles the connection to KEGG API through wsdl
KoMapper handles reactions, pathways and compounds retrieval on Ko IDs 
"""
from DuctApe.Common.CommonThread import CommonThread
from DuctApe.Common.utils import get_span
from SOAPpy import WSDL
import Queue
import logging
import os
import threading
import time
import urllib

__author__ = "Marco Galardini"

################################################################################
# Log setup

logger = logging.getLogger('Kegg')

################################################################################
# Classes

class MapParser(object):
    '''
    Takes an HTML of a Kegg map and returns a list of ready-to-use html lines
    '''
    def __init__(self,content):
        self.html = content
        self.map = []
        self.parse()
        
    def parse(self):
        b = False
        for l in self.html.split('\n'):
            l = l.lstrip().rstrip().strip()
            if '<map' in l[:4]:
                b = True
                self.map.append(l)
            elif '<area' in l[:6] and b:
                self.map.append(l)
            elif '</map' in l[:5] and b:
                self.map.append(l)
                break
            
        return self.map

class KeggAPI(object):
    '''
    Class KeggAPI
    Connects to KEGG API and performs various tasks
    Fail-safe: if a request fails it tries again and again
    All the results are stored in the attribute result, as well as the inputs
    '''
    def __init__(self):
        self._apiurl = 'http://soap.genome.jp/KEGG.wsdl'
        self._keggserv = None
        self.clean()
    
    def clean(self):
        self.input = None
        self.result = None
    
    def connect(self, retries=3):
        '''
        Connect to KEGG API
        If it fails it tries again (retries)
        Returns True if it worked, False otherwise
        '''
        logging.debug('KEPP API url: %s'%self._apiurl)
        attempts = 0
        while True:
            try:
                self._keggserv = WSDL.Proxy(self._apiurl)
                logging.debug('Connection to KEGG API successful')
                return True
            except:
                attempts += 1
                logging.debug('Connection to KEGG API failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('Could not connect to KEGG API')
                    return False

    def getTitle(self, entry, retries=3):
        '''
        Get the title of a specific KEGG object
        '''
        attempts = 0
        while True:
            try:
                self.input = entry
                logging.debug('Looking for title for KEGG entry %s'%entry)
                self.result = self._keggserv.btit(entry).strip().split(';')
                return
            except:
                attempts += 1
                logging.debug('btit failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('btit failed!')
                    raise Exception('btit request failed')
    
    def getReactions(self, ko_id, retries=3):
        '''
        Get the reaction IDs for a given KO entry
        '''
        attempts = 0
        while True:
            try:
                self.input = ko_id
                logging.debug('Looking for KEGG reactions from %s'%ko_id)
                self.result = self._keggserv.get_linkdb_by_entry(ko_id, 'reaction')
                return
            except:
                attempts += 1
                logging.debug('get_linkdb_by_entry failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_linkdb_by_entry failed!')
                    raise Exception('get_linkdb_by_entry request failed')
                
    def getPathways(self, re_id, retries=3):
        '''
        Get the pathway IDs for a given reaction
        '''
        attempts = 0
        while True:
            try:
                self.input = re_id
                logging.debug('Looking for KEGG pathways from %s'%re_id)
                self.result = self._keggserv.get_pathways_by_reactions([re_id])
                return
            except:
                attempts += 1
                logging.debug('get_pathways_by_reactions failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_pathways_by_reactions failed!')
                    raise Exception('get_pathways_by_reactions request failed')
    
    def getPathwaysByComp(self, co_id, retries=3):
        '''
        Get the pathway IDs for a given compound
        '''
        attempts = 0
        while True:
            try:
                self.input = co_id
                logging.debug('Looking for KEGG pathways from %s'%co_id)
                self.result = self._keggserv.get_pathways_by_compounds([co_id])
                return
            except:
                attempts += 1
                logging.debug('get_pathways_by_compounds failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_pathways_by_compounds failed!')
                    raise Exception('get_pathways_by_compounds request failed')
    
    def getReactionsFromPath(self, path_id, retries=3):
        '''
        Get the reaction IDs for a given pathway
        '''
        attempts = 0
        while True:
            try:
                self.input = path_id
                logging.debug('Looking for KEGG reactions from %s'%path_id)
                self.result = self._keggserv.get_reactions_by_pathway(path_id)
                return
            except:
                attempts += 1
                logging.debug('get_reactions_by_pathway failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_reactions_by_pathway failed!')
                    raise Exception('get_reactions_by_pathway request failed')
                
    def getCompoundsFromPath(self, path_id, retries=3):
        '''
        Get the compound IDs for a given pathway
        '''
        attempts = 0
        while True:
            try:
                self.input = path_id
                logging.debug('Looking for KEGG compounds from %s'%path_id)
                self.result = self._keggserv.get_compounds_by_pathway(path_id)
                return
            except:
                attempts += 1
                logging.debug('get_compounds_by_pathway failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_compounds_by_pathway failed!')
                    raise Exception('get_compounds_by_pathway request failed')
                    
    def getColoredPathway(self, path_id, obj_list, color_list, retries=3):
        '''
        Get the colored pathway and return the picture as a string
        If it fails, an exception is thrown
        '''
        attempts = 0
        while True:
            try:
                self.input = path_id
                logging.debug('Looking for KEGG colored map from %s'%path_id)
                url = self._keggserv.color_pathway_by_objects(path_id,
                                                      obj_list,[],color_list)
                sock=urllib.urlopen(url)
                content = sock.read()
                sock.close()
                self.result = content
                return
            except:
                attempts += 1
                logging.debug('color_pathway_by_objects failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('color_pathway_by_objects failed!')
                    raise Exception('color_pathway_by_objects request failed')
    
    def getURLColoredPathway(self, path_id, obj_list, color_list, retries=3):
        '''
        Get the URL of the colored pathway and return its content
        If it fails, an exception is thrown
        '''
        attempts = 0
        while True:
            try:
                self.input = path_id
                logging.debug('Looking for KEGG colored map URL from %s'%path_id)
                url =  self._keggserv.get_html_of_colored_pathway_by_objects(
                                                      path_id,
                                                      obj_list,[],color_list)
                self.result = url
                return
            except:
                attempts += 1
                logging.debug('get_html_of_colored_pathway_by_objects failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_html_of_colored_pathway_by_objects failed!')
                    raise Exception('get_html_of_colored_pathway_by_objects request failed')
                
    def getHTMLColoredPathway(self, path_id, obj_list, color_list, retries=3):
        '''
        Get the URL of the colored pathway and return its content
        If it fails, an exception is thrown
        '''
        attempts = 0
        while True:
            try:
                self.input = path_id
                logging.debug('Looking for KEGG colored map URL from %s'%path_id)
                url =  self._keggserv.get_html_of_colored_pathway_by_objects(
                                                      path_id,
                                                      obj_list,[],color_list)
                sock=urllib.urlopen(url)
                self.result = sock.read()
                sock.close()
                return
            except:
                attempts += 1
                logging.debug('get_html_of_colored_pathway_by_objects failed! Attempt %d'
                              %attempts)
                if attempts >= retries:
                    logging.warning('get_html_of_colored_pathway_by_objects failed!')
                    raise Exception('get_html_of_colored_pathway_by_objects request failed')

class KeggColor(object):
    '''
    Class KeggColor
    Holds the color information to be passed to MapsFetcher
    One object for each pathway
    '''
    def __init__(self, path, reactions={}, compounds={}):
        self.path = path 
        self.reactions = reactions
        self.compounds = compounds
    
    def setReactions(self, reactions):
        self.reactions = reactions
        
    def setCompounds(self, compounds):
        self.compounds = compounds
        
    def getAll(self):
        '''
        Returns a tuple --> objects, color
        '''
        objs = [x for x in self.reactions]
        colors = [self.reactions[x] for x in self.reactions]
        objs += [x for x in self.compounds]
        colors += [self.compounds[x] for x in self.compounds]
        
        return objs,colors
        
class KeggDetails(object):
    '''
    Class KoDetails
    All the informations returned by Mappers are contained here
    '''
    def __init__(self):
        # Details
        self.ko = None
        self.react = None
        self.comp = None
        self.path = None
        # Links
        self.koreact = None
        self.comppath = None
        self.pathreact = None
        self.pathcomp = None
        # Maps
        self.pathmaps = None
        
    def setDetails(self, ko=None, react=None, comp=None, path=None):
        self.ko = ko
        self.react = react
        self.comp = comp
        self.path = path
        
    def setLinks(self, koreact=None, comppath=None, pathreact=None, pathcomp=None):
        self.koreact = koreact
        self.comppath = comppath
        self.pathreact = pathreact
        self.pathcomp = pathcomp
    
    def setMaps(self, maps):
        self.pathmaps = maps
    
    def getKO(self):
        return self.ko
    
    def getReact(self):
        return self.react
    
    def getComp(self):
        return self.comp
    
    def getPath(self):
        return self.path
    
    def getKOLinks(self):
        return self.koreact
    
    def getCompLinks(self):
        return self.comppath
    
    def getPathLinks(self):
        return self.pathreact, self.pathcomp
    
    def getMaps(self):
        return self.pathmaps

class BaseKegg(CommonThread):
    def __init__(self, threads=5, queue=Queue.Queue()):
        CommonThread.__init__(self,queue)
        
        # Kegg connection
        self.handlers = []
        self.numThreads = threads
        
    def connect(self):
        '''
        Starts N connections to Kegg API
        Return False if something goes wrong
        '''
        for i in range(self.numThreads):
            obj = KeggAPI()
            if not obj.connect():
                return False
            self.handlers.append(obj)
        
        return True
    
    def cleanHandlers(self):
        for handler in self.handlers:
            handler.clean()
            
class BaseMapper(BaseKegg):
    def __init__(self, threads=5, avoid=[], queue=Queue.Queue()):
        BaseKegg.__init__(self, threads=threads, queue=queue)

        # Skip these
        self.avoid = avoid
        
        # Results
        self.reactdet = {}
        self.pathdet = {}
        self.pathreact = {}
        self.pathcomp = {}
        self.pathmap = {}
        self.compdet = {}
        
        # Output
        self.result = None
        
    def getReactDetails(self):
        for piece in get_span(self.reactdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for react in piece:
                if react in self.avoid:
                    continue
                
                obj = threading.Thread(
                            target = self.handlers[piece.index(react)].getTitle,
                            args = (react,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                self.reactdet[handler.input] = handler.result
                
    def getPathDetails(self):
        for piece in get_span(self.pathdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for path in piece:
                if path in self.avoid:
                    continue
                
                obj = threading.Thread(
                            target = self.handlers[piece.index(path)].getTitle,
                            args = (path,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                self.pathdet[handler.input] = handler.result
    
    def getMapsDetails(self):
        for piece in get_span(self.pathdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for path in piece:
                if path in self.avoid:
                    continue
                
                obj = threading.Thread(
                            target = self.handlers[piece.index(path)].getHTMLColoredPathway,
                        args = (path,[],[],))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                parser = MapParser(handler.result)
                self.pathmap[handler.input] = parser.map
    
    def getPathReactions(self):
        for piece in get_span(self.pathdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for path in piece:
                obj = threading.Thread(
                            target = 
                            self.handlers[piece.index(path)].getReactionsFromPath,
                            args = (path,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                for react in handler.result:
                    if handler.input not in self.pathreact:
                        self.pathreact[handler.input] = []
                    self.pathreact[handler.input].append(react)
                    if react not in self.reactdet:
                        self.reactdet[react] = None
                        
    def getPathCompounds(self):
        for piece in get_span(self.pathdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for path in piece:
                obj = threading.Thread(
                            target = 
                            self.handlers[piece.index(path)].getCompoundsFromPath,
                            args = (path,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                for comp in handler.result:
                    if handler.input not in self.pathcomp:
                        self.pathcomp[handler.input] = []
                    self.pathcomp[handler.input].append(comp)
                    if comp not in self.compdet:
                        self.compdet[comp] = None
                        
    def getCompDetails(self):
        for piece in get_span(self.compdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for comp in piece:
                if comp in self.avoid:
                    continue
                
                obj = threading.Thread(
                            target = self.handlers[piece.index(comp)].getTitle,
                            args = (comp,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                self.compdet[handler.input] = handler.result

class KoMapper(BaseMapper):
    '''
    From a list of KO IDs returns various details in an object
    KO --> title and details
    KO --> reactions (and titles)
    reactions --> pathways (and titles)
    pathways --> reactions, compounds (with titles)
    maps --> for each pathway, the html maps (!!!)
    '''
    
    _statusDesc = {0:'Not started',
               1:'Connection to KEGG',
               2:'Fetching reactions',
               3:'Fetching pathways',
               4:'Fetching pathways content',
               5:'Fetching details on KEGG entries',
               6:'Crafting results'}
    
    _substatuses = [2,3,4,5]
    
    def __init__(self, ko_list, threads=5, avoid=[], queue=Queue.Queue()):
        BaseMapper.__init__(self, threads=threads, avoid=avoid, queue=queue)
        # Kegg
        self.ko = ko_list
        
        # Results
        self.kodet = {}
        self.koreact = {}
        self.reactpath = {}
    
    def getKOdet(self):
        for piece in get_span(self.ko, self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for ko in piece:
                if ko in self.avoid:
                    continue
                
                obj = threading.Thread(
                            target = self.handlers[piece.index(ko)].getTitle,
                            args = (ko,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                self.kodet[handler.input] = handler.result
                
    def getReactions(self):
        for piece in get_span(self.ko, self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for ko in piece:
                obj = threading.Thread(
                            target = self.handlers[piece.index(ko)].getReactions,
                            args = (ko,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                for react in handler.result:
                    if 'original' in react.type:
                        if handler.input not in self.koreact:
                            self.koreact[handler.input] = []
                        self.koreact[handler.input].append(react.entry_id2)
                        # Is this reaction new?
                        if react.entry_id2 not in self.reactdet:
                            self.reactdet[react.entry_id2] = None
    
    def getPathways(self):
        for piece in get_span(self.reactdet.keys(), self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for react in piece:
                obj = threading.Thread(
                            target = self.handlers[piece.index(react)].getPathways,
                            args = (react,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                if len(handler.result) == 0:
                    continue
                if handler.input not in self.reactpath:
                    self.reactpath[handler.input] = []
                for path in handler.result:
                    self.reactpath[handler.input].append(path)
                    # A new pathway?
                    if path not in self.pathdet:
                        self.pathdet[path] = None
    
    def run(self):
        self.updateStatus()
        if not self.connect():
            self.sendFailure('Could not connect to KEGG')
            return
        
        # Reactions
        self._maxsubstatus = len(self.ko)
        self.updateStatus()
        try:
            self.getReactions()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Related pathways...
        self._maxsubstatus = len(self.reactdet)
        self.updateStatus()
        try:
            self.getPathways()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Pathways contents...
        # 1. Reactions
        self._maxsubstatus = len(self.pathdet)
        self.updateStatus()
        try:
            self.getPathReactions()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # 2. Compounds
        self._maxsubstatus = len(self.pathdet)
        try:
            self.getPathCompounds()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # KO details
        self._maxsubstatus = len(self.ko)
        self.updateStatus()
        try:
            self.getKOdet()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Pathway details
        self._maxsubstatus = len(self.pathdet)
        try:
            self.getPathDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Pathway HTML maps (!!!)
        self._maxsubstatus = len(self.pathdet)
        try:
            self.getMapsDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Reaction details
        self._maxsubstatus = len(self.reactdet)
        try:
            self.getReactDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Compound details
        self._maxsubstatus = len(self.compdet)
        try:
            self.getCompDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Prepare the output object
        self.updateStatus()
        self.result = KeggDetails()
        self.result.setDetails(self.kodet, self.reactdet,
                               self.compdet, self.pathdet)
        self.result.setLinks(koreact=self.koreact, pathreact=self.pathreact, 
                             pathcomp=self.pathcomp)
        self.result.setMaps(self.pathmap)

class CompMapper(BaseMapper):
    '''
    From a list of CO IDs returns various details in an object
    CO --> title and details
    CO --> pathways (and titles)
    pathways --> reactions, compounds (with titles)
    maps --> for each pathway, the html maps (!!!)
    '''
    
    _statusDesc = {0:'Not started',
               1:'Connection to KEGG',
               2:'Fetching pathways',
               3:'Fetching pathways content',
               4:'Fetching details on KEGG entries',
               5:'Crafting results'}
    
    _substatuses = [2,3,4]
    
    def __init__(self, co_list, threads=5, avoid=[], queue=Queue.Queue()):
        BaseMapper.__init__(self, threads=threads, avoid=avoid, queue=queue)
        # Kegg
        self.co = co_list
        
        # Results
        self.comppath = {}
        
    def getPathways(self):
        for piece in get_span(self.co, self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for co_id in piece:
                obj = threading.Thread(
                            target = self.handlers[piece.index(co_id)].getPathwaysByComp,
                            args = (co_id,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                if len(handler.result) == 0:
                    continue
                if handler.input not in self.comppath:
                    self.comppath[handler.input] = []
                for path in handler.result:
                    self.comppath[handler.input].append(path)
                    # A new pathway?
                    if path not in self.pathdet:
                        self.pathdet[path] = None
    
    def run(self):
        self.updateStatus()
        if not self.connect():
            self.sendFailure('Could not connect to KEGG')
            return
        
        # Related pathways...
        self._maxsubstatus = len(self.co)
        self.updateStatus()
        try:
            self.getPathways()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Pathways contents...
        # 1. Reactions
        self._maxsubstatus = len(self.pathdet)
        self.updateStatus()
        try:
            self.getPathReactions()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # 2. Compounds
        self._maxsubstatus = len(self.pathdet)
        try:
            self.getPathCompounds()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Pathway details
        self._maxsubstatus = len(self.pathdet)
        self.updateStatus()
        try:
            self.getPathDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Pathway HTML maps (!!!)
        self._maxsubstatus = len(self.pathdet)
        try:
            self.getMapsDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Reaction details
        self._maxsubstatus = len(self.reactdet)
        try:
            self.getReactDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Compound details
        self._maxsubstatus = len(self.compdet)
        try:
            self.getCompDetails()
        except Exception, e:
            self.sendFailure(e.message)
            return
        self.cleanHandlers()
        self.resetSubStatus()
        
        # Prepare the output object
        self.updateStatus()
        self.result = KeggDetails()
        self.result.setDetails(react=self.reactdet,
                               comp=self.compdet, path=self.pathdet)
        self.result.setLinks(comppath= self.comppath, pathreact=self.pathreact, 
                             pathcomp=self.pathcomp)
        self.result.setMaps(self.pathmap)

class MapsFetcher(BaseKegg):
    '''
    Class MapsFetcher
    Download colored Kegg maps (png or URLs)
    Input: color_objs (KeggColor list), picture, urls, prefix
    Output: tuple(list of png filenames, list of URLs)
    '''
    
    _statusDesc = {0:'Not started',
               1:'Making room',
               2:'Connection to KEGG',
               3:'Fetching maps (pictures)',
               4:'Fetching maps (URLs)'}
    
    _substatuses = [3,4]
    
    def __init__(self, color_objs, pictures=True, URLs=False, prefix='', 
                 threads=5, queue=Queue.Queue()):
        BaseKegg.__init__(self, threads=threads, queue=queue)
        
        self.colors = color_objs
        self.pictures = bool(pictures)
        self.HTMLs = bool(URLs)
        
        self._keggroom = None
        self._prefix = prefix 
        
        # Outputs
        self.pics = []
        self.pages = []
        self.result = (self.pics, self.pages)
    
    def makeRoom(self,location=''):
        '''
        Creates a tmp directory in the desired location
        '''
              
        # KEGG database path
        try:
            path = os.path.abspath(location)
            path = os.path.join(path, 'tmp')
            try:os.mkdir(path)
            except:pass
            path = os.path.join(path, 'keggmaps')
            try:os.mkdir(path)
            except:pass
            path = os.path.join(path, self._prefix)
            self._keggroom = path
            os.mkdir(path)
        except:
            logger.debug('Temporary directory creation failed! %s'
                          %path)
    
    def getMaps(self):
        for piece in get_span(self.colors, self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for kmap in piece:
                path = kmap.path
                objs,colors = kmap.getAll()
                print path, objs, colors
                
                obj = threading.Thread(
                        target = self.handlers[piece.index(kmap)].getColoredPathway,
                        args = (path,objs,colors,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                fname = os.path.join(self._keggroom,handler.input)
                fname = fname+'.png'
                fOut = open(fname,'w')
                fOut.write(handler.result)
                fOut.close()
                self.pics.append(fname)
    
    def getPages(self):
        for piece in get_span(self.colors, self.numThreads):
            self.cleanHandlers()
            self._substatus += self.numThreads
            if self._substatus > self._maxsubstatus:
                self._substatus = self._maxsubstatus
            self.updateStatus(sub=True)
            
            threads = []
            for kmap in piece:
                path = kmap.path
                objs,colors = kmap.getAll()
                
                obj = threading.Thread(
                        target = self.handlers[piece.index(kmap)].getURLColoredPathway,
                        args = (path,objs,colors,))
                obj.start()
                threads.append(obj)
            time.sleep(0.01)
            while len(threads) > 0:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
            for handler in self.handlers:
                if not handler.result:
                    continue
                self.pages.append(handler.result)
    
    def run(self):
        self.updateStatus()
        self.makeRoom()
        
        self.updateStatus()
        if not self.connect():
            self.sendFailure('Could not connect to KEGG')
            return
        
        if self.pictures:
            self._maxsubstatus = len(self.colors)
            self.updateStatus()
            try:
                self.getMaps()
            except Exception, e:
                self.sendFailure(e)
                return
            self.cleanHandlers()
            self.resetSubStatus()
        else:
            self.updateStatus(send=False)
        
        if self.HTMLs:
            self._maxsubstatus = len(self.colors)
            self.updateStatus()
            try:
                self.getPages()
            except Exception, e:
                self.sendFailure(e)
                return
            self.cleanHandlers()
            self.resetSubStatus()
        else:
            self.updateStatus(send=False)

class KeggNet(CommonThread):
    pass