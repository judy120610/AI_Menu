
import os
from utils import generate_menu_candidates

def test_ingredients():
    # Test Case 1: Distinct Ingredient (Fish)
    ingredients_1 = ["고등어", "무"]
    print(f"\n--- Testing with: {ingredients_1} ---")
    menus_1 = generate_menu_candidates(ingredients_1, [])
    print(f"Menus: {menus_1}")
    
    # Test Case 2: Distinct Ingredient (Ham/Cheese)
    ingredients_2 = ["햄", "치즈"]
    print(f"\n--- Testing with: {ingredients_2} ---")
    menus_2 = generate_menu_candidates(ingredients_2, [])
    print(f"Menus: {menus_2}")

if __name__ == "__main__":
    test_ingredients()
