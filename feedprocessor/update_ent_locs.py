import wikipedia
import time, sys
from pprint import pprint
from pymongo import MongoClient

def get_coordinates_from_wikipedia(ent_name, coordinates=[], seen=[]):
    try:
        latitude, longitude = wikipedia.page(ent_name).coordinates
        coordinates.append({"latitude":float(latitude),"longitude": float(longitude)})

    except wikipedia.exceptions.DisambiguationError as e:
        count = 0
        for item in e.options:
            seen.append(item)
            if item not in seen:
                if count < 3 and count < len(e.options):
                    coord = get_coordinates_from_wikipedia(item, coordinates, seen)
                    count += 1
        pass

    except wikipedia.exceptions.HTTPTimeoutError as e:
        print("In danger of ban")
        time.sleep(5)
        coord = get_coordinates_from_wikipedia(ent_name, coordinates)

    except:
        pass

    finally:
        time.sleep(1)

    return coordinates

def search_places_and_insert_coordinates(places, list_of_unmatched_entities):
    #search from localdb for places
    #then search from wikipedia if place not found

    for entity in list_of_unmatched_entities:
        exists = places.find({"location": entity}).count()
        if exists < 1:
            coordinates = get_coordinates_from_wikipedia(entity, coordinates=[])
            inserted_id = places.insert_one({"location":entity, "coordinates":coordinates}) 
        else:
            pass
        
    return "it is finished"

def get_and_process_entities(library, places):
    items = library.find({})
    entities = [item['entities'] for item in items]
    list_of_entities = [item['entity'] for entity in entities for item in entity]

    list_of_unmatched_entities = list(set(list_of_entities))

    search_places_and_insert_coordinates(places, list_of_unmatched_entities)

    return "I say it is finished"


if __name__ == "__main__":
    from settings.db import library, places
    library = client.alexandria.library
    places = client.alexandria.places
    get_and_process_entities(library, places)
