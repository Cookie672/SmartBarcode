from pathlib import Path
import pandas as pd
from utils import fetch

#Input Based
searchcol = input("Enter the column to search: ")
searchval = input("Enter the value to search for: ")
returncol = input("Enter the column to return: ")
try:
    result = fetch(searchcol, searchval, returncol)
    print(f"Result: {result}")
except Exception as e:
    print(f"An error occurred: {e}")