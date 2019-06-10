import random
from threading import Thread, RLock
from queue import Queue
import os
import time
import pandas as pd
import numpy as np

L = [f for f in os.listdir('./Dataset.csv') if f[:6] == 'attack']
frames=[]
for el in L :
    frames.append(pd.read_csv('./Dataset.csv/'+el+''))

database = pd.concat(frames)

database.iloc[[i for i in range(len(database))],0]= [i for i in range(len(database))]

database =database.to_numpy()

batchs = Queue(100)
verrou = RLock()

def file_len(f):
    i=0
    for i, l in enumerate(f):
        pass
    f.seek(0,0)
    return i + 1

def visit_line(line):
    l=line[:-2].split(" ")

    res = database[int(l[0])]
    for i in range(1,len(l)):
        res = np.vstack((res,database[int(l[i])]))

    return res,(np.hstack((np.zeros(len(res)-1,dtype=int),int(database[int(l[-1]),-1]))))

compteur={0:0, 1:0, 2:0, 4:0, 8:0, 16:0}
def fit(tmp):
    a,b=tmp
    compteur[b[-1]]+=1


def entrainement(file_name):

    f = open(file_name)
    l=[line for _,line in enumerate(f)]
    f.close()
    random.shuffle(l)
    for line in l:
        tmp = visit_line(line)
        fit(tmp)

entrainement('sets/test_x')
entrainement('sets/validation_x')
print(compteur)
