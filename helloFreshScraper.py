import requests
from bs4 import BeautifulSoup
from array import *
from pymongo import MongoClient
import time

#Establish DB connection
client = MongoClient("mongodb://127.0.0.1:27017")
client.server_info()
db = client.recipe_database
headers = {'User-Agent': 'Mozilla/5.0'}

#Get collection of HelloFresh Links
linkCollection = db['hf_links']

#Establish connection to recipes collection
recipeCollection = db['recipes']

#Method used to convert list to dictionary: give credit
def Convert(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct

#Parse recipe page
def parsePage(URL):
    #Generate HTML content of page
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    #Get recipe name
    title = soup.find(property="og:title").get("content")
    #Get recipe image
    image = soup.find(property="og:image").get('content')

    #Find elements with p tag for ingredients
    ingredients = soup.find_all("p")
    #Pop first two elements (known to not be ingredient elements)
    ingredients.pop(0)
    ingredients.pop(0)

    #Create conditional to see if link is parsable
    ableToInsert = False

    #Get the ingredients from element list, always given a class tag, but tag differes per recipe
    ingredientsList = []
    for i in ingredients:
        if "class" in str(i):
            try:
                ingredientsList.append(str(i.contents[0]))
                ableToInsert = True
            except:
                print("...")

    #Reverse list for proper key/value formatting
    ingredientsList.reverse()

    #Gets the cuisine of the dish by searching through the soup and extracting a cuisne element
    cuisine = str(soup)
    try:
        cuisine = cuisine.split("recipeCuisine",1)[1]
        cuisine = cuisine.split("</script>",1)[0]
        cuisine = cuisine.replace('}', '')
        cuisine = cuisine.replace(':', '')
        cuisine = cuisine.replace('"', '')
    except:
        cuisine = 'ERROR'


    #Stage document for insertion to collection
    toInsert = {
        "name" : title,
        "image" : image,
        "ingredients" : Convert(ingredientsList),
        "cuisine": cuisine,
        "link": URL }

    #Insert document into recipe collection if link was parsable and title does not exist in collection
    if ableToInsert:
        try:
            if (recipeCollection.find_one({"name": title}) is None):
                recipeCollection.insert_one(toInsert)
        except:
            print("Error adding recipe to DB")

    #Debug
    #print(title)
    #print(len(ingredientsList))

cursor = linkCollection.find({}, {"_id":0,"link":1})
for document in cursor:
    try:
        parsePage(document.get("link"))
    except:
        print("ERROR ADDING RECIPE")
