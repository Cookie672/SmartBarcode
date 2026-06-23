from flask import Flask, jsonify, request, render_template
import pandas as pd
import tkinter as tk
import threading
import socket
import qrcode
from pathlib import Path


# GLOBALS

current_id = 1
csv_lock = threading.Lock()

student_loaded = False


app = Flask(__name__)


# CSV
CSV_PATH = Path(__file__).with_name("DataCSV.csv")

#FETCH FUNCTION
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


# FLASK ROUTES

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/current")
def current():

    global current_id

    # name = fetch("id", current_id, "Name")
    # class1 = fetch("id", current_id, "Class")
    # section = fetch("id", current_id, "Section")
    # meal = fetch("id", current_id, "Meal Seeker")
    # status = fetch("id", current_id, "Status")
    row = fetch_row_safe("id", current_id)


    # if name is None or class1 is None or section is None or meal is None or status is None:
    if row is None:    
        return jsonify({
            "id":"",
            "name":"Not Found",
            "class":"",
            "section":"",
            "meal":"",
            "status":""
        })

    return jsonify({
        "id": row["id"],
        "name": row["Name"],
        "class": row["Class"],
        "section": row["Section"],
        "meal": row["Meal Seeker"],
        "status": row["Status"]
    })


@app.route("/ok", methods=["POST"])
def ok():

    global current_id
    global student_loaded

    if not student_loaded:
        return "No student loaded", 400

    update_safe(
        "id",
        current_id,
        "Status",
        "Taken"
    )

    print(
        f"ID {current_id} marked Taken"
    )

    return "Success"

# GUI

def create_gui():

    global current_id

    root = tk.Tk()

    root.title("Controller")

    root.geometry("300x250")

    label = tk.Label(
        root,
        text="Enter ID"
    )

    label.pack()

    entry = tk.Entry(root)

    entry.pack()

    current_label = tk.Label(
        root,
        text="No Student Loaded",
        justify="left"
    )

    current_label.pack()

    def refresh_display():

        global current_id
        global student_loaded

        if student_loaded:
            row = fetch_row_safe("id", current_id)

            if row is not None:

                current_label.config(
                    text=
                    f"ID: {row['id']}\n"
                    f"Name: {row['Name']}\n"
                    f"Class: {row['Class']}\n"
                    f"Section: {row['Section']}\n"
                    f"Status: {row['Status']}"
                )

        root.after(1000, refresh_display)


    def load():

        global current_id
        global student_loaded

        try:

            new_id = int(
                entry.get()
            )

            row = fetch_row_safe("id", new_id)

            if row is None:
                 print("Invalid ID")
                 return
            current_id = new_id

            

            current_label.config(
                text=
                f"ID: {row['id']}\n"
                f"Name: {row['Name']}\n"
                f"Class: {row['Class']}\n"
                f"Section: {row['Section']}\n"
                f"Status: {row['Status']}"
            )

            student_loaded = True
            print(
                "Loaded",
                current_id
            )

        except ValueError:
             print("Invalid ID")

    def reset_all():

        global student_loaded
        global current_id
        

        try:
            with csv_lock:
                df = pd.read_csv(CSV_PATH)

                df.loc[
                    df["Status"] == "Taken",
                    "Status"
                ] = "Not Taken"

                df.to_csv(
                    CSV_PATH,
                    index=False
                )

            current_label.config(
                text="No Student Loaded"
            )
            
            student_loaded = False
            current_id=1
            print(
                "All statuses reset"
            )

        except Exception as e:

            print(
                "Reset failed:",
                e
            )


    button = tk.Button(
        root,
        text="LOAD",
        command=load
    )

    button.pack()

    reset_button = tk.Button(
        root,
        text="RESET ALL",
        command=reset_all
    )

    reset_button.pack()


    refresh_display()
    root.mainloop()


# QR GENERATION

def get_ip():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:
        s.connect(("8.8.8.8",80))
        ip = s.getsockname()[0]

    except:
        ip = "127.0.0.1"

    s.close()

    return ip


ip = get_ip()

url = f"http://{ip}:5000"

print("Phone URL:")
print(url)

img = qrcode.make(url)

img.save("qr.png")

print("QR saved as qr.png")


# START SERVER THREAD

server_thread = threading.Thread(
    target=lambda:
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False
        )
)

server_thread.daemon = True

server_thread.start()


# START GUI

create_gui()