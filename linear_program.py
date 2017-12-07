#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 23:42:06 2017

@author: zhonghao
"""

from hungarian_method import construct_bipartite
import numpy as np
import csv
from time import time

x = 0

def printA(A):
    Alist = A.astype(int).tolist()
    for row in Alist:
        print(''.join(list(map(str, row))))
        
def constructA(numNLeft, numNRight, edgeLeft):
    edgeIndexPtr = [0] # 0 as place holder
    for i in range(1, numNLeft+1):
        edgeIndexPtr.append(edgeIndexPtr[-1] + len(edgeLeft[i]))
    A = np.zeros((numNLeft+numNRight, edgeIndexPtr[-1]))
    for i in range(0, numNLeft):
        for j in range(len(edgeLeft[i+1])):
            A[i][edgeIndexPtr[i]+j] = 1
            A[edgeLeft[i+1][j]-1][edgeIndexPtr[i]+j] = 1
    #printA(A)
    return A, edgeIndexPtr
            
def makeTableau(A):
    tableau = np.ndarray((A.shape[0]+1, A.shape[1]+A.shape[0]+2))
    slack = np.zeros((A.shape[0]+2))
    slack[-1] = 1
    for i in range(A.shape[0]):
        slack[i] = 1
        tableau[i] = np.concatenate((A[i], slack))
        slack[i] = 0
    slack[-1] = 0
    slack[-2] = 1
    tableau[-1] = np.concatenate((np.zeros((A.shape[1]))-1, slack))
    return tableau

def pivot(tableau):
    global x
    while(np.min(tableau[-1, 0:(tableau[-1].shape[0]-2)]) < 0):
        x += 1
        col = np.argmin(tableau[-1][0:tableau[-1].shape[0]-2])
        np.seterr(divide='ignore')
        row = -1
        q = np.inf
        for i in range(tableau.shape[0]-1):
            if tableau[i][col] > 0.:
                if tableau[i][-1] / tableau[i][col] < q:
                    q = tableau[i][-1] / tableau[i][col] 
                    row = i
        if row == -1:
            break
        #print(row, col, tableau[row][col])
        if tableau[row][col] != 1.:
            tableau[row] = tableau[row] / tableau[row][col]
        for i in range(tableau.shape[0]):
            if i != row:
                tableau[i] += -tableau[i][col] * tableau[row]
        #print(tableau)
    return tableau

def solve_edge_recur(tab, x, level):
    noneZeros = []
    for i in range(tab.shape[-1]-2):
        if tab[level][i] != 0 and x[i] == -1:
            noneZeros.append(i)
    for i in range(2**len(noneZeros)):
        for j in range(len(noneZeros)):
            x[noneZeros[j]] = np.float((i >> j) & 1)
        if np.matmul(tab[level, 0:(tab.shape[1]-2)], x) == tab[level][-1]:
            '''
            print(tab[level, 0:(tab.shape[1]-2)])
            print(x)
            print(np.matmul(tab[0:(tab.shape[0]-1), 0:(tab.shape[1]-2)], x))
            print(np.matmul(tab[level, 0:(tab.shape[1]-2)], x), tab[level][-1], level)
            print(' ')
            '''
            if level == tab.shape[0] - 2:
                return x
            else:
                ret = solve_edge_recur(tab, x, level+1)
                if len(ret) != 0:
                    return ret
        for j in range(len(noneZeros)):
            x[noneZeros[j]] = -1
    return []
        
    
def solve_edge(tab):
    x = np.zeros((tab.shape[1]-2)) - 1
    for i in range(tab.shape[1]-2):
        if tab[-1][i] > 0.:
            x[i] = 0
    return solve_edge_recur(tab, x, 0)
    
    
    
def LP(i, numNLeft, numNRight, edgeLeft, f):
    t1 = time()
    A, edgeIndexPtr = constructA(numNLeft, numNRight, edgeLeft)
    tableau = makeTableau(A)
    t2 = time()
    final_tableau = pivot(tableau)
    t3 = time()
    #edgeSolved = solve_edge(final_tableau)
    t4 = time()
    
    M = {}
    '''
    temp = 0
    for i in range(A.shape[1]):
        if edgeSolved[i] == 1:
            while(edgeIndexPtr[temp] <= i):
                temp += 1
            M[temp] = edgeLeft[temp][i-edgeIndexPtr[temp-1]]
    '''
    t5 = time()
    f.writerow([str(i), str(t2-t1), str(t3-t2), str(t4-t3), str(t5-t1), str(x)])
    return M

def main():
    fileName = 'linear_log.csv'
    file = open(fileName, 'w')
    f = csv.writer(file, delimiter=',')
    f.writerow(['nodes number', 'make tableau time', 'pivoting time', 'equation solving time', 'total time', 'pivoting steps'])
    for i in range(1, 201):
        print(i)
        numNLeft = i
        numNRight = i
        edgeLeft, edgeRight = construct_bipartite(numNLeft, numNRight, incidentRate = 1, disperseRate = 0)
        matchings = LP(i, numNLeft, numNRight, edgeLeft, f)
    file.close()
    

if __name__ == "__main__":
    main()