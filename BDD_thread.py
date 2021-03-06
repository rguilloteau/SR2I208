#!/usr/bin/env python
# coding: utf-8

import os
import time
import pandas as pd
import numpy as np
from random import shuffle
from threading import Thread, RLock
from queue import Queue

tmp = int(input("Exemple ? (0 pour non, 1 pour oui) : "))

L = [f for f in os.listdir('./Dataset.csv') if f[:6] == 'attack']
frames=[]
for el in L :
    frames.append(pd.read_csv('./Dataset.csv/'+el+''))

database = pd.concat(frames)

database.iloc[[i for i in range(len(database))],0]= [i for i in range(len(database))]

database = database.sort_values(['BSM'])
database=database.dropna()
list_recv = [database[database['Identifiant du destinataire'] == x] for x in database['Identifiant du destinataire'].unique()]

global N
N=500

EXEMPLE = (tmp==1)


batchs = Queue(100)
verrou = RLock()

def create_batch(k):

    #If there are not enough data (smaller than N) send only one batch
    if len(list_recv[k])<=N:

        tmp_x=[]

        for i in range(len(list_recv[k])-1):
            if list_recv[k].iloc[i,-1]==0:
                tmp_x.append(int(list_recv[k].iloc[i,0]))

        tmp_x.append(list_recv[k].iloc[-1, 0])

        batchs.put([tmp_x,int(list_recv[k].iloc[-1,-1])], block=True)

    else:
        compteur = 0
        i = 0
        tmp_x=[]

        while(compteur<N and i<(len(list_recv[k])-1)):
            if list_recv[k].iloc[i,-1]==0:
                tmp_x.append(int(list_recv[k].iloc[i,0]))
                compteur+=1
            i+=1


        if i==(len(list_recv[k])-1):
            batchs.put([tmp_x+[int(list_recv[k].iloc[i, 0])], int(list_recv[k].iloc[i, -1])])

        else:
            for j in range (i,len(list_recv[k])):
                if len(tmp_x)==N:
                    batchs.put([tmp_x+[int(list_recv[k].iloc[j, 0])],int(list_recv[k].iloc[j, -1])], block=True)
                    tmp_x.pop(0)

                if len(tmp_x)<N:
                    if list_recv[k].iloc[j,-1]==0:
                        tmp_x.append(int(list_recv[k].iloc[j, 0]))


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
            for i in range(1,2):
                create_batch(i)
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
        compteur={0:0, 1:0, 2:0, 4:0, 8:0, 16:0}
        tx = open("test_x", "w")
        vx = open("validation_x", "w")
        while not fini or not batchs.empty():
            with verrou:
                if batchs.empty():
                    continue
                else:
                    batch_x, batch_y = batchs.get(block=True)
            if (compteur[batch_y]%5!=0):
                for i in range(len(batch_x)):
                    tx.write(str(int(batch_x[i]))+" ")
                tx.write("\n")

            else:
                for i in range(len(batch_x)):
                    vx.write(str(int(batch_x[i]))+" ")

                vx.write("\n")


            compteur[batch_y] += 1

            time.sleep(0)


        tx.close()
        vx.close()
        print(compteur)

creater = BatchCreater()
writer = BatchWriter()

creater.start()
writer.start()

creater.join()
writer.join()
