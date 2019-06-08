#!/usr/bin/env python
# coding: utf-8

import os
import time
import pandas as pd
import numpy as np
from random import shuffle
from multiprocessing import Lock
from multiprocessing import Process
from multiprocessing.sharedctypes import Value
from multiprocessing import Queue
from ctypes import c_int

L = [f for f in os.listdir('./Dataset.csv') if f[:6] == 'attack']
frames=[]
for el in L :
    frames.append(pd.read_csv('./Dataset.csv/'+el+''))

database = pd.concat(frames)

database.sort_values(['BSM'])
database=database.dropna()
list_recv = [database[database['Identifiant du destinataire'] == x] for x in database['Identifiant du destinataire'].unique()]

fini = Value(c_int, 0)

batchs = Queue(100)
verrou = Lock()

def create_batch(k, N):


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




def batchCreater(fini, EXEMPLE, N):
    fini.value = 0
    if EXEMPLE :
        create_batch(1,100)
    else :
        index = [i for i in range(len(list_recv))]
        shuffle(index)
        for i in index:
            create_batch(i,N)
    fini.value = 1
    print("Coucou")
    #exit(1)



def batchWriter(fini):
    print("Coucou2")
    fx = open("batches_x", "w")
    fy = open("batches_y", "w")
    while (fini.value!=0) or not batchs.empty():
        print(fini.value)
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
    exit(1)

EXEMPLE = True
N=500
creater = Process(target=batchCreater, args=(fini, EXEMPLE, N))
writer = Process(target=batchWriter, args=(fini,))

creater.start()
writer.start()

creater.join()
writer.join()
