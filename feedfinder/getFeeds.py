import time
import sys
import os
import pymongo

import feedparser

from datetime import datetime
from pymongo import MongoClient
from pprint import pprint

def getFeeds():
    f = open("feeds.txt")

    feed_urls = []
    all_entries = []

    for feed_url in f:
        feed_urls.append(feed_url.strip())
    
    for feed_url in feed_urls:
        print("working with ", feed_url)
        parsed_feed = feedparser.parse(feed_url)
        entries = parsed_feed.entries
        for entry in entries:
            entry['source_title'] = parsed_feed['feed'].get("title", "Not Found")
            entry['source_link']  = parsed_feed['feed'].get("link", "#")
            entry['processed']    = False
            entry['date_added'] = datetime.now()
            all_entries.append(entry)

    return all_entries 
          

def insertUnprocessedFeeds():
    #put feeds in db if not in db
    entries = getFeeds()
    client  = MongoClient()
    db = client.alexandria
    try:
        result = db.unprocessedArticles.insert_many(entries, ordered=False)
    except pymongo.errors.BulkWriteError as bwe:
        pass

    done = "Unprocessed Articles updated on", datetime.now()
    print(done)

    return done
    
    
    

if __name__ == '__main__': 
    while True:
        try:
            insertUnprocessedFeeds()
            time.sleep(1*60*60)
        except KeyboardInterrupt:
            print('Goodbye Alvin.')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
         
 
