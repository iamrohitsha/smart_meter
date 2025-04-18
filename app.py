from flask import Flask, render_template, jsonify, request
import mysql.connector
import datetime

app = Flask(__name__)

# Function to create a new database connection
def get_db_connection():
    return mysql.connector.connect(
        host="192.168.98.132",  # Use Raspberry Pi IP
        user="pi",
        password="your_password",
        database="sensor_data"
    )

@app.route("/")
def index():
    db = get_db_connection()  # New connection for each request
    cursor = db.cursor(dictionary=True)

    # Fetch the latest entry
    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1")
    reading = cursor.fetchone()

    # Fetch the last 5 entries for history
    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 5")
    history = cursor.fetchall()

    cursor.close()
    db.close()  # Close connection to ensure fresh data is fetched

    return render_template("index.html", reading=reading, history=history)

@app.route("/update_relay", methods=["POST"])
def update_relay():
    relay_state = request.json.get("state")  # 1 for ON, 0 for OFF
    print("state: ",relay_state)
    if relay_state not in [0, 1]:
        return jsonify({"status": "error", "message": "Invalid relay state"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    # Insert a new row with only the relay state; RPi will overwrite this with voltage, etc.
    cursor.execute("INSERT INTO readings (relay) VALUES (%s)", (relay_state,))
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"status": "success", "relay_state": relay_state})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
