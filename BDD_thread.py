#!/usr/bin/env python
# coding: utf-8

import os
import time
import pandas as pd
import numpy as np
from random import shuffle
from threading import Thread, RLock
from queue import Queue

L = [f for f in os.listdir('./Dataset.csv') if f[:6] == 'attack']
frames=[]
for el in L :
    frames.append(pd.read_csv('./Dataset.csv/'+el+''))

database = pd.concat(frames)

database.sort_values(['BSM'])
database=database.dropna()
list_recv = [database[database['Identifiant du destinataire'] == x] for x in database['Identifiant du destinataire'].unique()]

global N
N=500
EXEMPLE = True


batchs = Queue(100)
verrou = RLock()

def create_batch(k):

    #If there are not enough data (smaller than N) send only one batch
    if len(list_recv[k])<=N:

        tmp_x=[]
        tmp_y=[]

        for i in range(len(list_recv[k])-1):
            if list_recv[k].iloc[i,-1]==0:
                tmp_x.append(list_recv[k].iloc[i,1:-1])
                tmp_y.append(0)

        tmp_y.append(int(list_recv[k].iloc[-1,-1]))
        tmp_x.append(list_recv[k].iloc[-1, 1:-1])

        batchs.put([tmp_x,tmp_y], block=True)

    else:
        compteur = 0
        i = 0
        tmp_x=[]
        tmp_y=[]

        while(compteur<N and i<(len(list_recv[k])-1)):
            if list_recv[k].iloc[i,-1]==0:
                tmp_x.append(list_recv[k].iloc[i,1:-1])
                tmp_y.append(0)
                compteur+=1
            i+=1


        if i==len(list_recv[k])-1:
            batchs.put([tmp_x+[list_recv[k].iloc[i, 1:-1]], int(tmp_y+[list_recv[k].iloc[i, -1]])])


        for j in range (i,len(list_recv[k])):
            if len(tmp_x)==N:
                batchs.put([tmp_x+[list_recv[k].iloc[j, 1:-1]],tmp_y+[int(list_recv[k].iloc[j, -1])]], block=True)
                tmp_x.pop(0)

            if len(tmp_x)<N:
                if list_recv[k].iloc[j,-1]==0:
                    tmp_x.append(list_recv[k].iloc[j, 1:-1])


class BatchCreater(Thread):
    """Va générer les batchs glissants"""

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global fini
        global N
        fini = False
        if EXEMPLE :
            N=100
            create_batch(1)
        else :
            index = [i for i in range(len(list_recv))]
            shuffle(index)
            for i in index:
                create_batch(i)
        fini = True

class BatchWriter(Thread):
    """Va écrire les batchs en mémoire"""

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global fini
        fx = open("batches_x", "w")
        fy = open("batches_y", "w")
        while not fini or not batchs.empty():
            with verrou:
                if batchs.empty():
                    continue
                else:
                    batch_x, batch_y = batchs.get(block=True)
            for i in range(len(batch_x)):
                tmp = batch_x[i].to_numpy()
                fx.write(str(tmp[1])+" ")
                for k in range(3,len(tmp)-1):
                    fx.write(str(tmp[k])+" ")
                fx.write("\n")
                fy.write(str(batch_y[i])+"\n")

            time.sleep(0)

            fx.write("\n")
            fy.write("\n")

        fx.close()
        fy.close()

creater = BatchCreater()
writer = BatchWriter()

creater.start()
writer.start()

creater.join()
writer.join()
