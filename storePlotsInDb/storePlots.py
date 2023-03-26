#ssh callable version of storePlots.ipynb

import numpy as np
import pandas as pd
import pymongo
import collections


#open DB
mongo_client = pymongo.MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.7.1")
book_plots_DB = mongo_client["book_plots_DB"]
book_plots = book_plots_DB["book_plots"]

def addFileToDB(filename = '../../data/NPZ/titleAndEncodedSummariesStrings1.npz'):
    loaded_arrays =  np.load(filename, allow_pickle = True)
    for book in loaded_arrays["arr_0"]:
        isbnArr = book[1].split(":") #some ISBNS have a name, then a colon, and then the isbn, these do not exist in the google api so ignore them
        if (len(isbnArr) > 1):
            continue
        title = book[0]
        plot = book[2]
        isbn = isbnArr[-1]
        book_plots.insert_one({"isbn": isbn, "title": title, "plot": plot})



def deleteEmptyPlotsFromDB():
	cursor = book_plots.find({})
	allBooks = [doc for doc in cursor]
	counter = 0
	for book in allBooks:
		if (book["plot"] == ""):
			counter += 1
			book_plots.delete_one({"isbn": book["isbn"], "title":book["title"], "plot": book["plot"]})
	print(f"Deleted {counter} books")
	



#ADDED FILES:
files = ["../data/titleAndEncodedSummariesStrings1.npz","../data/titleAndEncodedSummariesStrings2.npz", 
         "../data/titleAndEncodedSummariesStrings3.npz", "../data/titleAndEncodedSummariesStrings4.npz",
         "../data/titleAndEncodedSummariesStrings5.npz", "../data/titleAndEncodedSummariesStrings6.npz",
         "../data/titleAndEncodedSummariesStrings7.npz","../data/titleAndEncodedSummariesStrings8.npz", 
         "../data/titleAndEncodedSummariesStrings9.npz", "../data/titleAndEncodedSummariesStrings10.npz",
         "../data/titleAndEncodedSummariesStrings11.npz"]

#NON ADDED FILES:
nonAddedFiles = []

if __name__ == "__main__":
	for file in nonAddedFiles:  
		addFileToDB(file)
	deleteEmptyPlotsFromDB()