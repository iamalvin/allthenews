from bs4 import BeautifulSoup
import time
import sys
import os
import pymongo
import re
from datetime import datetime

from process_raws import *
from pprint import pprint

client = pymongo.MongoClient()
unprocessed_articles = client.alexandria.unprocessedArticles
info_palace = client.alexandria.info_palace

def get_and_process_feeds():
    unprocessed = unprocessed_articles.find({"$or":[{"located":{"$exists": False}}, {"located":False}]}, no_cursor_timeout=True ).sort("date_added", -1)
    processed = []

    for article in unprocessed:
        key = "summary"
        if key in article:
            about = get_locations(article)
            located_article = about
            del(located_article["_id"])

            try:
                added = info_palace.insert_one(located_article).inserted_id
                if added:
                    unprocessed_articles.update({"title": located_article["title"]}, {"$set": {"located": True}})
            except Exception as e:
                print(e)
                pass
        else:
            pass
    
    unprocessed.close()
    
    return processed

if __name__ == "__main__": 
    while True:
        try:
            processed = get_and_process_feeds()
            print(len(processed))
            time.sleep(1*60*60)
        except KeyboardInterrupt:
            print("Goodbye Sweet Prince")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
