from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

ONLY_THE_RECIPE_URL = 'https://recipescal.com/onlytherecipe'

service = Service(r'chromedriver-win64/chromedriver.exe')
options = Options()
options.add_argument('--headless')
options.add_argument('--log-level=3')  # Suppress logs
driver = webdriver.Chrome(service=service, options=options)

MEASUREMENTS = ['tablespoon', 'teaspoon', 'cup']


class Recipe():

    def __init__(self, recipe_name, recipe_url, recipe_tag):
        self.name = recipe_name
        self.recipe_url = recipe_url
        self.recipe_tag = recipe_tag

    def parse_ingredient(self, initial_string):
        processed_string = initial_string.split(',')[0]
        string_parts = processed_string.split(' ')

        end_of_quantity = 1

        using_measuremnet = False

        for measurement in MEASUREMENTS:
            if ((measurement in processed_string)
                    or (measurement+'s' in processed_string)):
                end_of_quantity = 2
                using_measuremnet = True

        if not using_measuremnet:
            for i, part in enumerate(string_parts):
                if (i == 1) and ('(' not in part):
                    break
                if (')' in part):
                    end_of_quantity = i+2

        quantity = " ".join(string_parts[0:end_of_quantity])
        ingredient_name = " ".join(string_parts[end_of_quantity:])
        return ingredient_name, quantity

    def get_ingredients(self) -> dict:
        global driver

        ingredients: dict[str, str] = {}

        scrape_url = ONLY_THE_RECIPE_URL + '?url=' + self.recipe_url
        driver.get(scrape_url)
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # for debugging
        # pretty_html = soup.prettify()
        # with open("parsed_output.html", "w", encoding="utf-8") as f:
        #     f.write(pretty_html)

        ingredient_divs = soup.select('div.text-md.mt-4')
        for div in ingredient_divs:
            div_text = div.get_text(strip=True)
            name, quantity = self.parse_ingredient(div_text)
            ingredients[name] = quantity

        return ingredients


class Ingredient():

    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity


class ShoppingList():

    def __init__(self):
        self.recipes: dict[str, Recipe] = {}
        self.shopping_list: dict[str, str] = {}

    def add_recipe(self, recipe_name: str, recipe_url: str, recipe_tag: str):
        new_recipe = Recipe(recipe_name, recipe_url, recipe_tag)
        self.recipes[new_recipe.name] = new_recipe

    def generate_list(self, query_tag):
        self.shopping_list.clear()
        for recipe_name, recipe in self.recipes.items():
            if recipe.recipe_tag == query_tag:
                ingredients = recipe.get_ingredients()
                for name, qunatity in ingredients.items():
                    self.shopping_list[name] = (self.shopping_list.get(name,
                                                                       "")
                                                + " "
                                                + qunatity)

    def __str__(self):
        out = "_"*50 + "\nThe Shopping List\n" + "-"*50
        for name, quantity in self.shopping_list.items():
            out += f"\n{name}: {quantity}"
        out += "_"*50
        return out
