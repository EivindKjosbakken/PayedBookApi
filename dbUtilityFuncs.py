import numpy as np
import pandas as pd
import pymongo
import collections



def getPlotFromIsbn(isbn: str, book_plots):
    """returns json object with keys 'title' and 'plot' and the representative title and plot. Note for some books, title is not available"""
    book = book_plots.find_one({"isbn": isbn})
    title = book.get("title", "")
    plot = book.get("plot", "")
    return {"title": title, "plot":plot}
