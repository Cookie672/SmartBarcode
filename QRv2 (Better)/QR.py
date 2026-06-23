from flask import Flask
import pandas as pd
import tkinter as tk
import threading
import socket
import qrcode
from pathlib import Path

# -----------------
# GLOBALS
# -----------------

csv_lock = threading.Lock()

app = Flask(__name__)

CSV_PATH = Path(__file__).with_name("DataCSV.csv")
QR_FOLDER = Path(__file__).with_name("qrs")

QR_FOLDER.mkdir(exist_ok=True)

# -----------------
# CSV FUNCTIONS
# -----------------

def fetch_row(searchcol, searchval):

    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    with csv_lock:
        df = pd.read_csv(CSV_PATH)

    matches = df[df[searchcol].astype(str) == str(searchval)]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


def update(searchcol,
           searchval,
           updatecol,
           newval):

    with csv_lock:

        df = pd.read_csv(CSV_PATH)

        matches = (
            df[searchcol]
            .astype(str)
            == str(searchval)
        )

        if not matches.any():
            return False

        df.loc[
            matches,
            updatecol
        ] = newval

        df.to_csv(
            CSV_PATH,
            index=False
        )

        return True


# -----------------
# NETWORK
# -----------------

def get_ip():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:
        s.connect(
            ("8.8.8.8", 80)
        )

        ip = s.getsockname()[0]

    except:
        ip = "127.0.0.1"

    s.close()

    return ip


IP = get_ip()

# -----------------
# QR GENERATION
# -----------------

def generate_all_qrs():

    df = pd.read_csv(CSV_PATH)

    count = 0

    for _, row in df.iterrows():

        student_id = row["id"]

        url = (
            f"http://{IP}:5000/"
            f"scan/{student_id}"
        )

        img = qrcode.make(url)

        img.save(
            QR_FOLDER /
            f"{student_id}.png"
        )

        count += 1

    print(
        f"{count} QR codes generated."
    )


# -----------------
# FLASK
# -----------------

@app.route("/")
def home():

    return """
    <h1>Meal System Running</h1>
    <p>Scan student QR codes.</p>
    """


@app.route("/scan/<int:student_id>")
def scan(student_id):

    row = fetch_row("id", student_id)

    if row is None:
        return f"""
        <h1>Student Not Found</h1>
        <p>ID: {student_id}</p>
        """

    return f"""
    <h1>Student Found</h1>

    <p><b>Name:</b> {row['Name']}</p>
    <p><b>ID:</b> {row['id']}</p>
    <p><b>Class:</b> {row['Class']}</p>
    <p><b>Section:</b> {row['Section']}</p>
    <p><b>Status:</b> {row['Status']}</p>

    <form action="/confirm/{student_id}" method="post">
        <button type="submit"
                style="font-size:24px;padding:15px;">
            Issue Meal
        </button>
    </form>
    """

@app.route("/confirm/<int:student_id>", methods=["POST"])
def confirm(student_id):

    row = fetch_row("id", student_id)

    if row is None:
        return "<h1>Student Not Found</h1>"

    if row["Status"] == "Taken":
        return f"""
        <h1>Meal Already Collected</h1>
        <p>{row['Name']}</p>
        """

    update(
        "id",
        student_id,
        "Status",
        "Taken"
    )

    return f"""
    <h1>Meal Issued Successfully</h1>

    <p>Name: {row['Name']}</p>
    <p>ID: {row['id']}</p>

    <a href="/">
        Back
    </a>
    """


# -----------------
# GUI
# -----------------

def create_gui():

    root = tk.Tk()

    root.title(
        "Meal Controller"
    )

    root.geometry(
        "300x150"
    )

    status_label = tk.Label(
        root,
        text=f"Server IP:\n{IP}"
    )

    status_label.pack(
        pady=10
    )

    def generate_qrs():

        generate_all_qrs()

        status_label.config(
            text=
            f"Generated QR Codes\nIP: {IP}"
        )

    def reset_all():

        with csv_lock:

            df = pd.read_csv(
                CSV_PATH
            )

            df["Status"] = (
                "Not Taken"
            )

            df.to_csv(
                CSV_PATH,
                index=False
            )

        status_label.config(
            text=
            "All Statuses Reset"
        )

        print(
            "Reset Complete"
        )

    qr_button = tk.Button(
        root,
        text="Generate QRs",
        command=generate_qrs
    )

    qr_button.pack(
        pady=5
    )

    reset_button = tk.Button(
        root,
        text="Reset All",
        command=reset_all
    )

    reset_button.pack(
        pady=5
    )

    root.mainloop()


# -----------------
# START SERVER
# -----------------

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

print(
    f"Server running at "
    f"http://{IP}:5000"
)

create_gui()