import pandas as pd
from pathlib import Path
from utils import fetch
import sys

name = input("Enter name: ")
try:
    meal = fetch("Name", name, "Meal Seeker")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)


if meal:
    print(f"{name} is a meal seeker.")
elif meal == False:
    print(f"{name} is not a meal seeker.")
else:
    print(f"{name} has a special case for meals.")
