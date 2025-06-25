import time
from models import ShoppingList


def main():
    SL = ShoppingList()
    SL.load_recipe_sets(fpath=r"recipe_sets.json")

    # need to wait for logging to complete :(
    while True:

        query_tag = input("Provide us the tag that scpecifies the recipes you want to create a list for: ")
        print("We are Getting your List Ready!")
        SL.generate_list(query_tag=query_tag)
        if len(SL.shopping_list) == 0:
            print("No recipes with the given tag were found")
            check = input("Do you want to try again with a new tag? Type Y to try again: ")
            if check == 'Y':
                continue
            else: 
                break
        else:
            print(SL)
            print("Enjoy Shopping!")
            break


if __name__ == "__main__":
    main()
