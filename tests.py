import unittest
import csv
from models import Ingredient


class RecipeTests(unittest.TestCase):
    """A class for testing the methods of the Recipe class"""
    def test_get_ingredients(self):
        self.assertTrue(True)


class IngredientTests(unittest.TestCase):
    """A class for testing the methods of the Ingredient class"""
    def test_add(self):
        quantity_1 = 1
        quantity_2 = 1
        ingredient_1 = Ingredient(f"{quantity_1} cheese")
        ingredient_2 = Ingredient(f"{quantity_2} cheese")
        new_quantity = ingredient_1 + ingredient_2
        expected_result = "1, 1 more"
        self.assertEqual(new_quantity, expected_result)
        
    def test_parse_ingredient(self):
        """Test the __parse_ingredient() method"""
        
        csv_path = r"test_cases\expected_test_results.csv"
        
        with open(csv_path, "r", newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)  # convert to a list to access by index
        
        
        fpath = r"test_cases\test_ingridients.txt"
        
        with open(fpath, "r") as file:
            for i, line in enumerate(file):
                ingredient = Ingredient(line.strip())
                
                self.assertEqual(ingredient.name, expected_name)
                self.assertEqual(ingredient.quantity, expected_quantity)
        
        
        
if __name__ == '__main__':
    print("-"*70, "\nRunning Tests...")
    unittest.main()
