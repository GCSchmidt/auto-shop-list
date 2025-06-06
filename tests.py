import unittest
from models import Recipe


class RecipeTests(unittest.TestCase):

    def test_get_ingredients(self):
        recipe = Recipe('www.recipe.com', 'cheesy pasta')
        actual_out = recipe.get_ingredients()
        expected_out = {'apple': 1}
        self.assertEqual(expected_out, actual_out)

 
if __name__ == '__main__':
    print("-"*70, "\nRunning Tests...")
    unittest.main()
