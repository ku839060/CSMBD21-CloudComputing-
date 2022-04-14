# -*- coding: utf-8 -*-
"""CSMBD21(Cloud computing coursework).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cEAWTiDwAh3TgB4SSiZxcNaXxBAoK8q8
"""

import pandas as pd
import csv

"""# Reading the datasets to datastructures, 
Pandas was used for this case for usability this also allowed for the checking of the results to ensure that they where correct.
"""

AComp_passenger_data_no_errorDF = pd.read_csv("/content/drive/MyDrive/University of reading/Sem 2/Big data and cloud computing/Cloud computing CourseWork/Data/AComp_Passenger_data_no_error.csv", header=None)
Top30_airports_LatLongDF = pd.read_csv("/content/drive/MyDrive/University of reading/Sem 2/Big data and cloud computing/Cloud computing CourseWork/Data/Top30_airports_LatLong.csv", header=None)

AComp_passenger_data_no_errorDF
#checking the dataset using pandas for visual aid.

"""# Reading and parsing the data"""

#opening the dataset
AComp_passenger_data_no_error = open('/content/drive/MyDrive/University of reading/Sem 2/Big data and cloud computing/Cloud computing CourseWork/Data/AComp_Passenger_data_no_error.csv')
#Top30_airports_LatLong = open('/content/drive/MyDrive/University of reading/Sem 2/Big data and cloud computing/Cloud computing CourseWork/Data/Top30_airports_LatLong.csv')

#reading the dataset
AComp_passenger_data_no_error_reader = csv.reader(AComp_passenger_data_no_error)
#Top30_airports_LatLong_reader = csv.reader(Top30_airports_LatLong)

#Parseing the data. for use within the mapper.
parsedata = []
for row in AComp_passenger_data_no_error_reader:
  parsedata.append(row)

"""# Mapper Phase Class"""

class Mapper(object):
  def __init__(self): super(Mapper, self).__init__()
  
  #the mapper function that assigns a key and a value to a list containing tuples.
  def mapper(self, datastructure, colum):
    TupleList = []
    for line in datastructure:
      TupleList.append(tuple( (line[colum], 1)))
    return TupleList

"""# Multithreading class functions

As the threading inbuilt does not allow for easy return of functions this function was used to facilitate this aspect.
"""

from threading import Thread

#this class allows for the returning of functions when using threading
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,args=(), kwargs={}, Verbose=None):
      Thread.__init__(self, group, target, name, args, kwargs)
      self._return = None

  #sets up the thread
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    #initalises the thread.
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

"""Multithreading mapper function to ensure that all the threads are completed before moving onto the reducing stage."""

def multithreadingmapper(datastructure,column,chunks):

  #breaking the data into chunks
  n = int((len(parsedata))/chunks)
  chunkeddata=[parsedata[i:i + n] for i in range(0, len(parsedata), n)]

  #creating threads for each of the chunks for the mapper to utilise
  #in this case four where used.
  listofmappedchunks = []
  for chunk in chunkeddata:
      chunkmappedthread = ThreadWithReturnValue(target = MapperObject.mapper,args = (chunk,column))
      chunkmappedthread.start()
      listofmappedchunks.append(chunkmappedthread.join())

  #combining the results of the threads into one single which can then be utilised by the reducer.
  Combinedmappedresult = []
  for mappedchunk in listofmappedchunks:
       Combinedmappedresult = Combinedmappedresult + mappedchunk

  return Combinedmappedresult

"""# Reduce Phase class"""

class Reducer(object):  
  def __init__(self):
          super(Reducer, self).__init__()

  # this function provides a reduced dictionary for use in the lower functions
  def reduct(self,TupleList):
    reductdict = {}
    for key, value in TupleList:
      reductdict[key] = reductdict.get(key,0) + value
    return reductdict

  #when standard reducing this sorts them by value as well
  def reducer(self,TupleList):

    reducerDict = self.reduct(TupleList)
    sorted_tuples = sorted(reducerDict.items(), key=lambda item: item[1],reverse = True)
    sorted_dict = {k: v for k, v in sorted_tuples}

    return list(sorted_dict.items())

  #this function returns only the highest key value, Used for highest number of flights
  def HighestReducer(self,TupleList):

    reducerDict = {}
    reducerDict = self.reduct(TupleList)
    HighestPassenger = max(reducerDict, key=reducerDict.get)

    return HighestPassenger

"""# Creating a mapper and reducer object"""

MapperObject = Mapper()
ReducerObject = Reducer()

"""# Task 1"""

#passing the colum related to flight from this is where multiple nodes of the mapper are used in threads
Combinedmappedresult = multithreadingmapper(parsedata,2,4)

#reducing the mapped results down. this function also sorts into decending order.
ReducerOutput = ReducerObject.reducer(Combinedmappedresult)

ReducerOutput

"""# task 2"""

#passing the colum related to Passengers from this is where multiple nodes of the mapper are used in threads
Combinedmappedresult = multithreadingmapper(parsedata,0,4)
#returning only the passenger that coccurs most frequently.
ReducerHighestOutput = ReducerObject.HighestReducer(Combinedmappedresult)
ReducerHighestOutput