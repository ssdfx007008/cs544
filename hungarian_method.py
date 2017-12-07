#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:40:39 2017

@author: zhonghao
"""

import random
import sys
import numpy as np
from scipy.stats import truncnorm

class node(object):
    def __init__(self, data):
        self.children = []
        self.data = data
        self.indicator = 0

def construct_bipartite(numNLeft, numNRight, incidentRate = 1, disperseRate = 0):
    mean = int(incidentRate * numNLeft)
    nodeLeft = list(range(1, numNLeft+1))
    edgeRight = {}
    edgeLeft = {}
    for i in range(1, numNLeft + 1):
        edgeLeft[i] = []
    if incidentRate == 1 or disperseRate == 0:
        for i in range(numNLeft + 1, numNLeft + numNRight+1):
            edgeRight[i] = random.sample(nodeLeft, k = mean)
            for item in edgeRight[i]:
                edgeLeft[item].append(i)
    else:     
        low = 0
        upp = numNLeft
        sd = disperseRate
        rightNodeNum = truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd).rvs(numNRight)
        for i in range(numNLeft + 1, numNLeft + numNRight+1):
            edgeRight[i] = random.sample(nodeLeft, k = round(np.asscalar(rightNodeNum[i-numNLeft-1])))
            for item in edgeRight[i]:
                try:
                    edgeLeft[item].append(i)
                except: 
                    pass
    return edgeLeft, edgeRight

def printPath(path):
    temp = []
    for item in path:
        temp.append(item.data)
    print('[%s]' %(', '.join(map(str, temp))))

def DFS(s, t, path):
    path.append(s)
    s.indicator = 1
    if s == t:
        return 1
    if len(s.children) == 0:
        path[-1].indicator = 0
        del path[-1]
        return 0
    for item in s.children:
        if item.indicator == 0:
            indicator = DFS(item, t, path)
            if indicator == 1:
                return 1
    path[-1].indicator = 0
    del path[-1]
    return 0
        
def printNode(Ns):
    for item in Ns:
        temp = []
        for ele in item.children:
            temp.append(ele.data)
        print('%d: [%s]' %(item.data, ', '.join(map(str, temp))))
    
        
def findAugmentingPath(numNLeft, numNRight, edgeLeft, M):
    s = node(-1)
    t = node(-2)
    nodes = []
    for i in range(0, numNLeft+numNRight+1):
        nodes.append(node(i))
    for i in range(1, numNLeft + 1):
        if i not in M:
            s.children.append(nodes[i])
            for item in edgeLeft[i]:
                try:
                    nodes[i].children.append(nodes[item])
                except:
                    pass
        else:
            for item in edgeLeft[i]:
                if item != M[i]:
                    nodes[i].children.append(nodes[item])
                else:
                    nodes[M[i]].children.append(nodes[i])
    for i in range(numNLeft + 1, numNLeft + numNRight+1):
        if len(nodes[i].children) == 0:
            nodes[i].children.append(t)
    augPath = []
    if 0 == DFS(s, t, augPath):
        return None
    dicPath = {}
    for i in range(len(augPath)):
        if augPath[i].data > 0 and augPath[i].data <= numNLeft:
            if augPath[i].data in dicPath:
                dicPath[augPath[i].data].append(augPath[i+1].data)
            else:
                dicPath[augPath[i].data] = [augPath[i+1].data]
        if augPath[i].data > numNLeft and augPath[i].data <= numNLeft+numNRight:
            if augPath[i+1].data > 0:
                dicPath[augPath[i+1].data] = [augPath[i].data]
    return dicPath

def exAdd(M, augPath):
    newM = {}
    for item in M:
        if item not in augPath:
            newM[item] = M[item]
        else:
            if M[item] not in augPath[item]:
                newM[item] = M[item]
    for item in augPath:
        if item not in M:
            newM[item] = augPath[item][0]
            if len(augPath[item]) > 1:
                sys.exit()
        else:
            for itemInItem in augPath[item]:
                if itemInItem != M[item]:
                    if item in newM:
                        sys.exit()
                    newM[item] = itemInItem
    return newM
                    
def hungrian(numNLeft, numNRight, edgeLeft):
    M = {}
    augPath = findAugmentingPath(numNLeft, numNRight, edgeLeft, M)
    while(augPath != None):
        M = exAdd(M, augPath)
        augPath = findAugmentingPath(numNLeft, numNRight, edgeLeft, M)        
    return M

def main():
    numNLeft = 5
    numNRight = 5
    edgeLeft, edgeRight = construct_bipartite(numNLeft, numNRight, incidentRate = 1, disperseRate = 0)
    matchings = hungrian(numNLeft, numNRight, edgeLeft)
    print(matchings)
    
if __name__ == "__main__":
    main()
