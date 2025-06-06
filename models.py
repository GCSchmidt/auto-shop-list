class Recipe():

    def __init__(self, recipe_url, name):
        self.name = name
        self.recipe_url = recipe_url

    def get_ingredients(self) -> dict:
        ingredients = {'apple': 1}
        return ingredients
