from pathlib import Path
import pandas as pd


CSV_PATH = Path(__file__).with_name("DataCSV.csv")

def fetch(searchcol: str, searchval, returncol: str, csvpath: str = CSV_PATH):
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"{CSV_PATH} not found")
    with csv_lock:
        df = pd.read_csv(csvpath)

    if searchcol not in df.columns:
        raise KeyError(f"Column '{searchcol}' not found in CSV")
    if returncol not in df.columns:
        raise KeyError(f"Column '{returncol}' not found in CSV")

    matches = df[df[searchcol].astype(str) == str(searchval)]
    if matches.empty:
        raise ValueError(f"No row found where {searchcol} == {searchval}")

    return matches.iloc[0][returncol]

def fetch_safe(searchcol: str, searchval, returncol: str, csvpath: str = CSV_PATH):
    try:
        return fetch(searchcol, searchval, returncol, csvpath)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
#READ ROW FUNCTION - (Efficiency)
def fetch_row(searchcol: str,
              searchval,
              csvpath: str = CSV_PATH):

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"{CSV_PATH} not found")

    with csv_lock:
        df = pd.read_csv(csvpath)

    if searchcol not in df.columns:
        raise KeyError(f"Column '{searchcol}' not found")

    matches = df[df[searchcol].astype(str) == str(searchval)]

    if matches.empty:
        raise ValueError(
            f"No row found where {searchcol} == {searchval}"
        )

    return matches.iloc[0].to_dict()

def fetch_row_safe(searchcol, searchval):

    try:
        return fetch_row(searchcol, searchval)

    except Exception as e:
        print(e)
        return None
    
#UPDATE FUNCTION
def update(searchcol: str,
           searchval,
           updatecol: str,
           newval,
           csvpath: str = CSV_PATH):
    with csv_lock:
        df = pd.read_csv(csvpath)

        if searchcol not in df.columns:
            raise KeyError(f"Column '{searchcol}' not found")

        if updatecol not in df.columns:
            raise KeyError(f"Column '{updatecol}' not found")

        matches = df[searchcol].astype(str) == str(searchval)

        if not matches.any():
            raise ValueError(
                f"No row found where {searchcol} == {searchval}"
            )

        df.loc[matches, updatecol] = newval

        df.to_csv(csvpath, index=False)


def update_safe(*args, **kwargs):

    try:
        update(*args, **kwargs)

    except Exception as e:
        print(f"Update error: {e}")

