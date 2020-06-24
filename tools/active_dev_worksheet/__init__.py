import networkx as nx
import gc
import datetime
import os
import collections

from pywintypes import com_error # pylint: disable=no-name-in-module
from itertools import zip_longest
import time

from .xlhelpers import *
from .redmine import api
from .adtable import *
        

def Save(wb, *a,**k):
    wb.Application.DisplayAlerts = False
    try:
        wb.SaveAs(*a,**k)
    finally:
        wb.Application.DisplayAlerts = True
    

def save_to_sharepoint(wb, fp):
    Save(wb, fp, CreateBackup=False, AddToMru=True)
    
    
def checkout(wb):
    # The check in/out process is REALLY
    # kludgy from VBA. Check out essentially never
    # works without waiting a short period of time
    # for ... something ... to connect.
    
    # Regardless, we can reliably
    # perform checkout by looping until it works.
    
    # 5 second timeout to be safe. 
    
    xl = wb.Application
    end = time.time() + 5  # 5 second timeout
    while True:
        try:
            xl.Workbooks.CheckOut(wb.FullName)
        except Exception:
            if time.time() > end:
                raise
            time.sleep(0.2)  # give it a chance to think
        else:
            return
    
def publish(wb):
    checkout(wb)
    wb.CheckInWithVersion(True, "", True, xlc.xlCheckInMajorVersion)

def make_graph(key):
    client = api.Client("issue.pbsbiotech.com",key)
    ad_issues = client.Issues.filter(status_id="*")
    ad_map = {i.id:i for i in ad_issues}

    # first graph - all issues
    g = nx.DiGraph()
    for i in ad_issues:
        iid = i.id
        g.add_node(iid)
        pid = i.parent
        if pid is not None:
            g.add_edge(pid, iid)

    if not nx.is_forest(g):  # should not be possible
        raise ValueError("Circles in graph :(") 
    
    # simple DFS impl for (parent, node) pair callbacks
    def _dfs_visit2(g, parent, visit, depth):
        for node in sorted(g.successors(parent)):
            visit(parent, node)
            _dfs_visit2(g, node, visit, depth + 1)
        
    def dfs_visit2(g, node, visit):
        visit(None, node)
        _dfs_visit2(g, node, visit, 1)
    
    # second graph - only what we care about
    # this routine loads all Active Development issues as well
    # as any children, regardless of milestone
    
    fv_active = 96  # sprint/milestone ID for software Active Development
    
    g2 = nx.DiGraph()
    def visit(parent, node):
        g2.add_node(node)
        if parent is not None:
            g2.add_edge(parent, node)
    
    for i in ad_issues:
        if i.fixed_version is None or i.fixed_version.id != fv_active:
            continue
        dfs_visit2(g, i.id, visit)

    return g2, ad_map

