#!/usr/bin/env python
# coding: utf-8

import os
import time
import pandas as pd
import numpy as np
from random import shuffle


L = [f for f in os.listdir('./Dataset.csv') if f[:6] == 'attack']
frames=[]
for el in L :
    frames.append(pd.read_csv('./Dataset.csv/'+el+''))

database = pd.concat(frames)

database.iloc[[i for i in range(len(database))],0]= [i for i in range(len(database))]

database=database.sort_values(['BSM'])
database=database.dropna()
list_recv = [database[database['Identifiant du destinataire'] == x] for x in database['Identifiant du destinataire'].unique()]

N=500



def create_batch(k):

    #If there are not enough data (smaller than N) send only one batch
    if len(list_recv[k])<=N:

        tmp_x=[]
        tmp_y=[]

        for i in range(len(list_recv[k])-1):
            if list_recv[k].iloc[i,-1]==0:
                tmp_x.append(list_recv[k].iloc[i,0])
                tmp_y.append(0.0)

        tmp_y.append(list_recv[k].iloc[-1,-1])
        tmp_x.append(list_recv[k].iloc[-1, 0])

        return [tmp_x], [tmp_y]

    else:
        batches_x = []
        batches_y = []
        compteur = 0
        i = 0
        tmp_x=[]
        tmp_y=[]

        while(compteur<N and i<(len(list_recv[k])-1)):



            if list_recv[k].iloc[i,-1]==0:
                tmp_x.append(list_recv[k].iloc[i,0])
                tmp_y.append(0.0)
                compteur+=1
            i+=1


        if i==len(list_recv[k])-1:
            return ([tmp_x+[list_recv[k].iloc[i, 0]]]),([tmp_y+[list_recv[k].iloc[i, -1]]])


        for j in range (i,len(list_recv[k])):
            if len(tmp_x)==N:
                batches_x.append((tmp_x+[list_recv[k].iloc[j, 0]]))
                batches_y.append((tmp_y+[list_recv[k].iloc[j, -1]]))
                tmp_x.pop(0)

            if len(tmp_x)<N:
                if list_recv[k].iloc[j,-1]==0:
                    tmp_x.append(list_recv[k].iloc[j, 0])

        return batches_x, batches_y

from random import shuffle

batches_x=[]
batches_y=[]
EXEMPLE = True
if EXEMPLE:
    N=100
    temp_x, temp_y = create_batch(1)
    batches_x += temp_x
    batches_y += temp_y
else:
    for i in range(len(list_recv)):
        temp_x, temp_y = create_batch(i)
        batches_x += temp_x
        batches_y += temp_y

fx = open("batches_x", "w")
fy = open("batches_y", "w")

index = [i for i in range(len(batches_x))]
shuffle(index)

for i in index:
    for j in range(len(batches_x[i])):
        tmp = batches_x[i][j]
        fx.write(str(tmp)+" ")
        fy.write(str(batches_y[i][j])+" ")
    fx.write("\n")
    fy.write("\n")

fx.close()
fy.close()
