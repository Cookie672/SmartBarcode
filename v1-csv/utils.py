from pathlib import Path
import pandas as pd


CSV_PATH = Path(__file__).with_name("DataCSV.csv")

#Main Abstraction
def fetch(searchcol: str, searchval, returncol: str, csvpath: str = CSV_PATH):
	df = pd.read_csv(csvpath)

	if searchcol not in df.columns:
		raise KeyError(f"Column '{searchcol}' not found in CSV")
	if returncol not in df.columns:
		raise KeyError(f"Column '{returncol}' not found in CSV")

	matches = df[df[searchcol].astype(str) == str(searchval)]
	if matches.empty:
		raise ValueError(f"No row found where {searchcol} == {searchval}")

	return matches.iloc[0][returncol]