import socket
import json
from datetime import datetime
import pymysql
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import ssl

# Paramètres du serveur
HOST = "0.0.0.0"
PORT = 5000

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

def get_db_connection():
    try:
        conn = pymysql.connect(
            user="root",
            password="qwertyDB", 
            host="localhost",
            database="data",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        print(f"Erreur connexion MariaDB: {e}")
        return None

# Serveur socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server is listening at {HOST}:{PORT}")

    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected to {addr}")
        with open("logs.txt", "a") as log_file:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                try:
                    # Décodage des données JSON
                    json_data = json.loads(data.decode("utf-8"))
                    temperature = json_data["temperature"]
                    humidity = json_data["humidity"]
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    pressure = json_data["pressure"]

                    # Log console
                    log = f"{timestamp} - Temperature: {temperature} °C, Humidity: {humidity}, Pressure: {pressure} %"
                    print(log)

                    # Connexion à la base de données et insertion
                    db_conn = get_db_connection()
                    if db_conn:
                        with db_conn.cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO sensor_data (datetime, temperature, humidity) VALUES (%s, %s, %s)",(timestamp, temperature, humidity)
                            )
                            cursor.execute(
                                "INSERT INTO BMP280_measurement (datetime, pressure) VALUES (%s, %s)",(timestamp, pressure)
                            )
                        db_conn.commit()
                        db_conn.close()

                    # Écriture dans le fichier log
                    log_file.write(log + "\n")

                except json.JSONDecodeError:
                    print("Error decoding JSON !")

# Flask API
app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)


# # Route pour afficher la page web
# @app.route("/")
# def index():
#     return render_template("index.html")

# # Route pour récupérer les données du capteur
# @app.route("/sensor-data")
# def sensor_data():
#     db_conn = get_db_connection()
#     if not db_conn:
#         return jsonify({"error": "DataBase connnexion error"}), 500

#     with db_conn.cursor() as cursor:
#         cursor.execute("SELECT datetime, temperature, humidity FROM sensor_data ORDER BY id DESC LIMIT 10")
#         data = [{"time": row["datetime"].strftime("%H:%M:%S"), "temperature": row["temperature"], "humidity": row["humidity"]} for row in cursor.fetchall()]

#     db_conn.close()
#     return jsonify(data)