import pymongo
from pymongo import MongoClient

#Establish DB connection
client = MongoClient("mongodb://127.0.0.1:27017")
client.server_info()
db = client.recipe_database
collection = db.recipe_links
#Create set of links
link_list = set([])
save = False

#Collect links until exit condition
while(True):
    inputLink = input("Enter Link: ")
    #To save in HelloFresh link collection
    if inputLink == "hf":
        save = True;
        collection = db.hf_links
        break
    #To save in BlueApron link collection
    elif inputLink == "ba":
        save = True;
        collection = db.ba_links
        break
    #To exit without saving
    elif inputLink == "EXIT":
        break
    link_list.add(inputLink)

#Total number of unique links added to database
added_links = 0

#Add all links in set to DB
if save:
    for i in link_list:
        #Check if link is already in collection
        if (collection.find_one({"link": str(i)}) is None):
            link = {
                'link' : i
            }
            collection.insert_one(link)
            added_links += 1

print(str(added_links) + " links added to database")
