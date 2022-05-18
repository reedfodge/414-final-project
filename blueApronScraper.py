import requests
from bs4 import BeautifulSoup
from array import *
from pymongo import MongoClient

#Establish DB connection
client = MongoClient("mongodb://159.89.226.89:27017")
client.server_info()
db = client.recipe_database
headers = {'User-Agent': 'Mozilla/5.0'}

#

#Parse recipe page
def parsePage(URL):
    #Get HTML of page
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    #Get recipe name
    title = soup.find(property="og:title").get("content")
    #Find list of ingredients
    ingredients = soup.find_all("li", itemprop="recipeIngredient")
    #Get recipe image
    image = soup.find(property="og:image").get('content')

    #Clean list of ingredients
    ingredientList = []
    for i in ingredients:
        #Get the measurement and count of the ingredient
        measurementCount = i.span.text.strip().split('\n')
        #Get the ingredient name
        i.span.decompose()
        i = i.text.strip()
        measurement = 'units'
        if(len(measurementCount) > 1):
            measurement = measurementCount[1]
        ingredientList.append([measurementCount[0], measurement, i])


    #Stage document for insertion to collection
    toInsert = {
        "name" : title,
        "image" : image,
        "ingredients" : ingredientList,
        "link": URL }



parsePage("https://www.blueapron.com/recipes/wonton-noodle-stir-fry-with-soft-boiled-eggs")
