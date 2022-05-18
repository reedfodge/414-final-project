import pandas as pd
from pymongo import MongoClient
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import random
import math
import sys
import math
from math import *
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples, silhouette_score


#Establish connection to MongoDB database
client = MongoClient("mongodb://127.0.0.1:27017")
client.server_info()
db = client.recipe_database
collection = db.recipes

#Creates dataframe of the recipes in database
documents = collection.find({})

#The collection of unique ingredients found in all recipes
unique_ingredients = ["chicken", "beef", "pasta", "shrimp", "rice", "onion", "potato", "mushroom", "corn", "salt"]
#A collection of recipes in a ['recipe_name', 'list of ingredients'] format
recipes = []
#A collection of just the lists of ingredients for each recipe
recipe_ingredients_list = []
#A collection of one-hot encoded lists of ingredients
encoded_ingredients_list = []
encoded_cuisines = []
unique_cuisines = []


#List of words that, if contained in an ingredient, will not be included
stop_words = ["sauce", "concentrate", "spice", "tablespoon", "cup", "ounce", "unit", "teaspoon", "seasoning", "salt", "pepper", "oil"]
#List of common words to group together similar ingredients
common_words = ["chicken", "beef", "pasta", "shrimp", "rice", "onion", "potato", "mushroom", "corn", "salt"]


#Populate the unique_ingredients, recipe_ingredients_list, and recipes list
def generate_lists():
    #Iterate over all documents in MongoDB recipe collection
    for d in documents:
        #A collection of all ingredients found in a recipe
        recipe_ingredients = []
        #An index to track the position in the raw ingredient list
        index = 0

        #Generate list of ingredients in recipe
        for ingredient in d["ingredients"]:
            #Get every other element in list since format is ['ingredient', 'measurement']
            #if index % 2 == 0:
                #Ensure data is clean, some HTML tags made their way into dataset

            #index = index+1
            string = str(ingredient).lower()
            if '<' not in ingredient:
                #Create checks for stop and common words
                is_stop_word = False
                is_common_word = False
                #Check if ingredient is a stop word
                for sw in stop_words:
                    if sw in string:
                        is_stop_word = True
                #Check if ingredient is a common word
                if not is_stop_word:
                    for cw in common_words:
                        if cw in string:
                            #Add common word to list of recipe's ingredients
                            recipe_ingredients.append(cw)
                            is_common_word = True
                #Adds ingredient if not stop or common word
                if not is_stop_word and not is_common_word:
                    recipe_ingredients.append(string)
        #Add unique recipe ingredients to unique_ingredients list
        for ingredient in recipe_ingredients:
            if ingredient not in unique_ingredients:
                unique_ingredients.append(ingredient)

        #Add recipe's list of ingredients to ingredients-only list
        recipe_ingredients_list.append(recipe_ingredients)

        #Create an element containing the name of the recipe and its formatted list of ingredients
        element = [d["name"], recipe_ingredients, d['cuisine']]
        #Add element to recipe list
        recipes.append(element)


#Generate a list of recipes as their one-hot encoded ingredient lists
def encode_ingredients():
    #Iterate over list of unique ingredients
    for ingredient_list in recipe_ingredients_list:
        encoded_ingredients = []
        for index in range(len(unique_ingredients)):
            #If the recipe contains a certain ingredient, its bit is set to one
            if unique_ingredients[index] in ingredient_list:
                encoded_ingredients.append(1)
            #If the recipe doesn't contain that ingredient, its bit is set to zero
            else:
                encoded_ingredients.append(0)
        #Added the encoded ingredients to list of recipes
        encoded_ingredients_list.append(encoded_ingredients)


#Populates the list of unique cuisines
def get_unique_cuisines():
    for r in recipes:
        if r[2] not in unique_cuisines:
            unique_cuisines.append(r[2])

#One-hot encodes the cuisines for each recipe
def encode_cuisine():
    for r in recipes:
        encoded_cuisine = []
        for i in range(len(unique_cuisines)):
            if r[2] in unique_cuisines[i]:
                encoded_cuisine.append(1)
            else:
                encoded_cuisine.append(0)
        encoded_cuisines.append(encoded_cuisine)


#Gets a list of the most used ingredients
def get_most_used_ingredients():
    for recipe in recipes:
        ingredient_list = recipe[1]
        for i in ingredient_list:
            index = unique_ingredients.index(i)
            ingredient_instances[index] = ingredient_instances[index]+1

#Populate matrix with instances of ingreident pairs:
def populate_matrix():
    #Iterate over all recipes
    for recipe in recipes:
        #Get the recipe's list of ingredients
        ingredient_list = recipe[1]
        #Iterate over list of unique ingredients
        for first_ingredient in unique_ingredients:
            #Get the position of the first ingredient
            first_ingredient_index = unique_ingredients.index(first_ingredient) - 1
            #Iterate over unique ingredients again, for comparison
            for second_ingredient in unique_ingredients:
                #Get position of second ingredient
                second_ingredient_index = unique_ingredients.index(second_ingredient) - 1
                #Determines if both ingredients are found in recipe, increments pair's position in matrix if so
                if first_ingredient in ingredient_list and second_ingredient in ingredient_list:
                    matrix[first_ingredient_index][second_ingredient_index] = matrix[first_ingredient_index][second_ingredient_index] + 1


#Normalizes the data in the matrix by taking the log of each value
def normalize_matrix():
    #Iterate over every matrix element
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            #Check if element is greater than 0 (log(0) = undefined)
            if matrix[i][j] > 0:
                if matrix[i][j] == 1:
                    matrix[i][j] == 0.2
                else:
                    matrix[i][j] = float(math.log(matrix[i][j]) * 3)


#Return the max instances of ingredient pairs in the format [same_ingredients, different_ingredients]
def get_matrix_max():
    max = [0,0]
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] > max[0] and i == j:
                max[0] = matrix[i][j]
            elif matrix[i][j] > max[1] and i != j:
                max[1] = matrix[i][j]
    return max

#Gets the euclidian distance between two points
def get_euclid_dist(x, y):
    return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

#Generates the heatmap based on the relationship matrix
def generate_heatmap():
    skip_ui = unique_ingredients
    print(len(unique_ingredients))
    print(len(skip_ui))
    for i in range(len(skip_ui)):
        if i % 5 != 0:
            skip_ui[i] = ''
    fig, ax = plt.subplots()
    im = ax.imshow(np.triu(matrix), cmap='hot', interpolation='nearest')
    #ax.set_xticks(np.arange(len(unique_ingredients)), labels=skip_ui)
    #ax.set_yticks(np.arange(len(unique_ingredients)), labels=skip_ui)
    #plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #         rotation_mode="anchor")
    ax.set_title("Ingredient Combinations")
    fig.tight_layout()
    plt.show()

#Finds the nearest recipe to a passed in recipe
def find_nearest(test):
    closest_index = sys.float_info.max
    index = 0
    recipe_distances = []
    df = pd.DataFrame(encoded_ingredients_list)
    pca = PCA(n_components=5)
    tf_pca = pca.fit_transform(df)
    pca_list = tf_pca.tolist()
    test = pca_list[250]
    for i in pca_list:
        distance = get_euclid_dist(test, i)
        recipe_distances.append({'recipe': recipes[index][0], 'distance': distance})
        index = index+1

    newlist = sorted(recipe_distances, key=lambda d: d['distance'])
    newlist = newlist[0:10]
    print("===== Most Similar Recipes =====")
    for i in newlist:
        print(i)


#Determines the number of clusters for the recipes
def cluster():
    df = pd.DataFrame(encoded_ingredients_list)
    pca = PCA(n_components=5)
    tf_pca = pca.fit_transform(df)
    df_pca = pd.DataFrame(tf_pca)
    print(df_pca[0])
    print(df_pca[1])
    plt.scatter(df_pca[0], df_pca[1], alpha=.3, color='red')
    #plt.show()
    sil_scores = [silhouette_score(df, KMeans(n_clusters=k).fit_predict(df)) for k in range(2,10)]
    index = 2
    max_index = 0
    print("Silhouette Scores")
    for i in sil_scores:
        print(str(index) + " : " + str(i))
        if i == max(sil_scores):
            max_index = index
        index = index+1
    print("Maximum silhouette score for " + str(max_index) + " clusters: " + str(max(sil_scores)))
    print("Number of unique cuisines: " + str(len(unique_cuisines)))

    model = KMeans(n_clusters=9)
    clusters = model.fit_predict(df)


if __name__ == "__main__":
    generate_lists()
    print("Lists Generated")
    encode_ingredients()
    get_unique_cuisines()
    encode_cuisine()
    random.shuffle(unique_ingredients)
    #A collection of every unique pairs of ingredients
    matrix = np.zeros((len(unique_ingredients), len(unique_ingredients)), dtype=float)
    populate_matrix()
    #print(get_matrix_max())
    normalize_matrix()
    #print(get_matrix_max())
    generate_heatmap()
