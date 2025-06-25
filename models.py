from __future__ import annotations
import time
import json
import os
import subprocess
import logging
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup



ONLY_THE_RECIPE_URL = 'https://recipescal.com/onlytherecipe'
MEASUREMENTS: list[str] = ["tablespoon", "tbsp"
                           "teaspoon", "tsp", 
                           "cup", 
                           "lb", "pounds", 
                           " g", "grams",
                           "oz", "ounce"
                           ]
BASICS: list[str] = ["salt", "pepper", "water", "flour", "oil"]

logging.basicConfig(
    filename="my_logfile.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

##########################################################
# OLD - Works
# service = Service(r'chromedriver-win64/chromedriver.exe')
# options = Options()
# options.add_argument('--headless')
# options.add_argument('--log-level=5')  # Suppress logs
# driver = webdriver.Chrome(service=service, options=options)
##########################################################

###########################################################
# NEW to surpress logging
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# chromedriver_path = r"chromedriver-win64/chromedriver.exe"
# null = open(os.devnull, 'w')

# # Start chromedriver manually on port 9515
# chromedriver_proc = subprocess.Popen(
#     [chromedriver_path, "--port=9515"],
#     stdout=null,
#     stderr=null,
#     stdin=null,
#     creationflags=subprocess.CREATE_NO_WINDOW  # Windows-specific: hides terminal window
# )

# # Wait for server to initialize
# time.sleep(1)

# # Configure Chrome options
# options = Options()
# options.add_argument("--headless")
# options.add_argument("--disable-logging")
# options.add_argument("--log-level=3")
# options.add_experimental_option("excludeSwitches", ["enable-logging"])

# # Connect to the running chromedriver
# driver = webdriver.Remote(
#     command_executor='http://127.0.0.1:9515',
#     options=options
# )

###########################################################


class Recipe():
    """
    A class for dealing with recipes accessed by URLs.
    """
    def __init__(self, recipe_name, recipe_url, recipe_tag) -> None:
        self.name = recipe_name
        self.recipe_url = recipe_url
        self.recipe_tag = recipe_tag

    def parse_ingredient(self, initial_string: str) -> tuple[str, str]:
        """
        Returns the ingredients name and qunatity as strings.
        If the ingredient is a basic, (None, None) is returned. 
        """

        # check if its a basic ingredient
        for basic in BASICS:
            if basic in initial_string:
                return None, None

        # processed_string = initial_string.split(',')[0]
        # string_parts = processed_string.split(' ')
        # end_of_quantity = 1
        # using_measuremnet = False
        # for measurement in MEASUREMENTS:
        #     if ((measurement in processed_string)
        #             or (measurement+'s' in processed_string)):
        #         end_of_quantity = 2
        #         using_measuremnet = True

        # if not using_measuremnet:
        #     for i, part in enumerate(string_parts):
        #         if (i == 1) and ('(' not in part):
        #             break
        #         if (')' in part):
        #             end_of_quantity = i+2

        quantity = 1
        ingredient_name = initial_string
        return ingredient_name, quantity

    def get_ingredients(self, driver: WebDriver) -> dict[str, str]:
        ingredients: dict[str, str] = {}

        scrape_url = ONLY_THE_RECIPE_URL + '?url=' + self.recipe_url
        try:
            driver.get(scrape_url)
            time.sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            logging.error("An error occurred while scraping the website", 
                          exc_info=True)
            return
        # for debugging
        # pretty_html = soup.prettify()
        # with open("parsed_output.html", "w", encoding="utf-8") as f:
        #     f.write(pretty_html)

        ingredient_divs = soup.select('div.text-md.mt-4')
        for div in ingredient_divs:
            div_text = div.get_text(strip=True)
            name, quantity = self.parse_ingredient(div_text)
            if ((name is not None) and (quantity is not None)):
                ingredients[name] = quantity

        return ingredients


class Ingredient():

    def __init__(self, input: str):
        self.name: str
        self.quantity: str
        self.__parse_ingredient(input)

    def __parse_ingredient(self, input: str):
        """Parses the input to get the name and quantity of the ingredient"""
        for basic in BASICS:
            if basic in input:
                self.name = None
                self.quantity = None
                return

        # TODO add better parsing
        
        self.quantity = "1"
        self.name = input

    def __add__(self, other: Ingredient) -> str:
        
        if self.name != other.name:
            msg = (f"Cannot add different ingredients:"
                   f"'{self.name}' and '{other.name}'")
            raise ValueError(msg)
        
        return self.quantity + ", " + other.quantity + " more"


class ShoppingList():

    def __init__(self):
        self.recipes: dict[str, Recipe] = {}
        self.shopping_list: dict[str, str] = {}

    def add_recipe(self, recipe_name: str, recipe_url: str, recipe_tag: str):
        new_recipe = Recipe(recipe_name, recipe_url, recipe_tag)
        self.recipes[new_recipe.name] = new_recipe

    def __generate_driver(self) -> WebDriver:
        # get things ready to search the web
        print("Creating WebDriver...")
        service = Service(r'chromedriver-win64/chromedriver.exe')
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--log-level=5')  # Suppress logs
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def generate_list(self, query_tag: str) -> None:

        driver = self.__generate_driver()

        self.shopping_list.clear()
        for recipe_name, recipe in self.recipes.items():
            if recipe.recipe_tag == query_tag:
                ingredients = recipe.get_ingredients(driver)
                for name, additional in ingredients.items():
                    # ingredient already in list
                    current_quantity = self.shopping_list.get(name, "")
                    if len(current_quantity) == 0:
                        # if item not yet in list
                        new_quantity = additional
                    else:
                        new_quantity = (current_quantity
                                        + ", "
                                        + additional
                                        + " more")
                    # update shopping list
                    self.shopping_list[name] = new_quantity

        # clean up after driver was
        driver.quit()

    def load_recipe_sets(self, fpath: str, query_tag: str = None) -> None:
        with open(fpath, "r") as f:
            data: dict = json.load(f)

        recipe_sets: dict = data["recipe_sets"]

        if query_tag is None:
            # load all sets
            for recipe_tag, new_recipes in recipe_sets.items():
                for i, recipe_url in enumerate(new_recipes):
                    self.add_recipe(f"recipe_{recipe_tag}_{i}",
                                    recipe_url,
                                    recipe_tag)
        else:
            # load specific set
            new_recipes: list = recipe_sets.get(query_tag, [])
            for i, recipe_url in enumerate(new_recipes):
                self.add_recipe(f"recipe_{query_tag}_{i}",
                                recipe_url,
                                query_tag)
     
    def __str__(self):
        out = "_"*50 + "\nThe Shopping List\n" + "-"*50
        for name, quantity in self.shopping_list.items():
            out += f"\n{name}"
        out += ("\n" + "_"*50)
        return out
