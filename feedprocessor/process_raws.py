import pymongo

from datetime import datetime
from update_ent_locs import get_coordinates_from_wikipedia 
from spacy.en import English

from utils import normalise

client = pymongo.MongoClient()
places = client.alexandria.places

parser = English()

def process_noun_phrases(raw):
    for ent in raw.ents:
        ent.merge(ent.root.tag_, ent.text, ent.label_)
    for np in list(raw.noun_chunks):
        while len(np) > 1 and np[0].dep_ not in ('advmod', 'amod', 'compound', 'det', 'prep'):
            np = np[1:]
        np.merge(np.root.tag_, np.text, np.root.ent_type_)

def get_heads(token, head_list):
    if token.head == token:
        add_token_to_list(token, head_list)
        return head_list
    else:
        add_token_to_list(token, head_list)
        return get_heads(token.head, head_list)

def add_token_to_list(token, head_list):
    if token.pos_ not in ['DET', 'PREP']:
        if token.dep_ in ["nsubj", "nsubjpass"]:
            head_list.append(token.orth_)
        else:
            head_list.insert(0, token.orth_)

def make_head_list(token):
    head_list = []
    return get_heads(token, head_list)

def find_sentences(raw):
    sentences = [sentence for sentence in raw.sents]
    return sentences

def process_appos(sentence):
    about_appos = []
    for token in sentence:
        if token.dep_ == "appos":
            key_token = token.head.orth_
            key_token.replace(".", " ")
            about_appos.append({"obj":key_token, "phrase" :key_token + " is " + token.orth_})
    return about_appos

def about_sentence(sentence, default_context): 

    try:
        text = sentence.text
    except IndexError:
        text = "empty" 

    entities = [{"entity":token.orth_, "locations":[]} for token in sentence if token.ent_type_ != ""]
    
    try:
        context = [token.orth_ for token in sentence if token.dep_  == "nsubj" and token.ent_type_ != ""][0]
    except IndexError:
        context = default_context

    get_appos = process_appos(sentence)
    about_sentence = []

    for token in sentence:
        if token.dep_ in ['nsubj','nsubjpass','iobj','iobjpass','dobj','dobjpass','pobj','pobjpass']:
            key_token  = token.orth_
            key_token.replace("." , " ")
            about_sentence.append({"obj": key_token, "phrase": " ".join(make_head_list(token))})

    about_sentence = about_sentence + get_appos
    

    return {"text":text, "details":about_sentence, "context": context, "entities":entities}

def process_article(raw, date_added):
    process_noun_phrases(raw)
    sentences = find_sentences(raw)
    try:
        default_context = [ent.orth_ for ent in raw.ents if ent.label_ != ""][0]
    except IndexError:
        try:
            default_context = [ent.orth_ for ent in raw.ents][0]
        except IndexError:
            default_context = "unknown"     
        
    processed = []
    for sentence in sentences:
        about_sent = about_sentence(sentence, default_context)
        about_sent["date_added"] = date_added
        processed.append(about_sent)

    return processed

def merge_ents(raw):
    for ent in raw.ents:
        ent.merge(ent.root.tag_, ent.text, ent.label_)

def get_ents(raw):
    entities=[]
    for ent in raw.ents:
        entities.append(ent.orth_)
    return entities

def get_location(ent):
    exists = places.find({"location": ent}).count()
    if exists < 1:
        coordinates = get_coordinates_from_wikipedia(ent, coordinates=[])
        inserted_id = places.insert_one({"location":ent, "coordinates":coordinates})
    else:
        pass
    locations = places.find_one({"location":ent})
    
    coord_list = locations['coordinates']

    entity_coordinates = []
    for item in coord_list:
        lon =item['longitude']
        lat =item['latitude']
        result = {"loc":{"type":"Point", "coordinates":[lon, lat]}}
        entity_coordinates.append(result)

    return entity_coordinates

def get_locations(article):
    #find entities
    #entities are in article['summary']

    article['title'] = normalise(article['title'])
    article['summary'] = normalise(article['summary'])

    raw = parser(article['title']+ " " +article['summary'])
    merge_ents(raw)
    entities = get_ents(raw)
    #locate entities
    #places is my entity databases
    entity_list=[]
    for ent in entities: 
        if ent.lower not in  ["mister", "mr.", "mr"]:
            locations = get_location(ent)
            entity_list.append({"entity":ent, "locations":locations})
    #add entities to article
    article['entities'] = entity_list
    article['added_by'] = "system"

    #return article
    return article
