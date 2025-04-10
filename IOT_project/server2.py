import socket
import ssl
import json
from datetime import datetime
import pymysql
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS

# Paramètres du serveur
HOST = "0.0.0.0"
PORT = 5000

# Chemins vers tes certificats (PEM)
CERT_FILE = "cert.pem"
KEY_FILE  = "key.pem"
# (Optionnel) pour l’authentification mutuelle client
# CLIENT_CA = "client_cert.pem"

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

# --- Configuration du contexte TLS ---
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
# Pour exiger un certificat client (MTLS), décommente :
# context.verify_mode = ssl.CERT_REQUIRED
# context.load_verify_locations(cafile=CLIENT_CA)

# --- Serveur TCP enveloppé SSL ---
with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as bindsock:
    bindsock.bind((HOST, PORT))
    bindsock.listen(1)
    print(f"Serveur TLS à l’écoute sur {HOST}:{PORT}")

    # Dès qu’on accepte, on « wrap » le socket dans TLS
    with context.wrap_socket(bindsock, server_side=True) as serverssl:
        conn, addr = serverssl.accept()
        print(f"Nouvelle connexion TLS de {addr}")
        with conn, open("logs.txt", "a") as log_file:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    # Décodage JSON
                    payload = json.loads(data.decode("utf-8"))
                    temperature = payload["temperature"]
                    humidity    = payload["humidity"]
                    pressure    = payload["pressure"]
                    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Log console et fichier
                    log = (f"{timestamp} - Temp: {temperature} °C, "
                           f"Hum: {humidity} %, Pres: {pressure} hPa")
                    print(log)
                    log_file.write(log + "\n")

                    # Insertion en base
                    db = get_db_connection()
                    if db:
                        with db.cursor() as cur:
                            cur.execute(
                                "INSERT INTO sensor_data (datetime, temperature, humidity) "
                                "VALUES (%s, %s, %s)",
                                (timestamp, temperature, humidity)
                            )
                            cur.execute(
                                "INSERT INTO BMP280_measurement (datetime, pressure) "
                                "VALUES (%s, %s)",
                                (timestamp, pressure)
                            )
                        db.commit()
                        db.close()
                except json.JSONDecodeError:
                    print("Erreur JSON reçue !")

app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
