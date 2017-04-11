# allthenews
An aggregator of as much news as I can find to process and order 

This python script gathers as many feeds as it can, from the feedfinder/feeds.txt, it stores them in a mongo database.

I run a variety of processing on the articles in the database (processor is in the feedprocessor directory).

So far:
* use spacy to recognise the entities in the summaries and articles
* use wikipedia to get locations from as many entities as it can
* stores the located entities in a different collection. for easy consumption

Planned:
* find a better way of ordering and classifying the data.
* add sentiment processing to the processing queue
 

this script requires/depends on:
* wikipedia
* spacy
* feedparser
* beautifusoup
* pymongo

I used Mongo but a database is a database, Planning to migrate from.
Any help or comment is appreciated.
