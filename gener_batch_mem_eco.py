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
    res = database.iloc[int(float(l[0])),:-1].to_numpy()
    for i in range(1,len(l)):
        res = np.vstack((res,database.iloc[int(float(l[i])), :-1]))

    return res,(np.hstack((np.zeros(len(res)-1,dtype=int),int(database.iloc[int(float(l[-1])),-1]))))


def get_line(f, index):
    for i, line in enumerate(f):
        if i == index:
            f.seek(0,0)
            return visit_line(line)

def fit(tmp):
    a,b=tmp
    print(a.shape,b[-1])


def entrainement(file_name):

    f = open(file_name)
    l=[i for i in range(file_len(f))]
    random.shuffle(l)
    for line in l:
        tmp = get_line(f, line)
        fit(tmp)

entrainement('sets/test_x')
