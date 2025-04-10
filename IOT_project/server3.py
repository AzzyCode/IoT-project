from flask import Flask, render_template, jsonify, redirect, url_for, request
import pymysql
import hashlib
import socket
import os

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

app = Flask(__name__)

@app.route('/index')
def index():
    db_conn = get_db_connection()
    if not db_conn:
        return "Erreur de connexion à la base de données"

    try:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT datetime, temperature, humidity FROM sensor_data ORDER BY id DESC LIMIT 10")
            data = cursor.fetchall()
        
        if not data:
            print("⚠️ Aucune donnée trouvée dans la base de données.")
            
        db_conn.close()
        return render_template("index.html", sensor_data=data)

    except Exception as e:
        print(f"❌ Erreur SQL: {e}")
        return f"Erreur SQL: {e}"

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db_conn = get_db_connection()
    if not db_conn: 
        return "Erreur de connexion à la base de données"

    try:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE name = %s", (username,))
            user = cursor.fetchone()
        
        db_conn.close()
        if user and hashlib.sha256(password.encode()).hexdigest() == user['password']:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="❌ Incorrect login , Please try again.")


    except Exception as e:
        print(f"❌ Erreur SQL: {e}")
        return f"Erreur SQL: {e}"
    
@app.route('/signup')
def signup_page():
    return render_template('signup.html')


@app.route('/signupbis')
def signup_page_bis():
    return render_template('signupbis.html')

@app.route("/sensor-data")
def sensor_data():
    db_conn = get_db_connection()
    if not db_conn:
        return jsonify({"error": "Erreur de connexion à la base de données"}), 500

    try:
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT datetime, temperature, humidity FROM sensor_data ORDER BY id DESC LIMIT 100")
            sensor_data = cursor.fetchall()

            cursor.execute("SELECT pressure FROM BMP280_measurement ORDER BY id DESC LIMIT 100")
            pressure_data = cursor.fetchall()

            # Combine the rows
            data = []
            for s_row, p_row in zip(sensor_data, pressure_data):
                data.append({
                    "datetime": s_row["datetime"],
                    "temperature": s_row["temperature"],
                    "humidity": s_row["humidity"],
                    "pressure": p_row["pressure"]
                })

        if not data:
            print("⚠️ Aucune donnée trouvée.")

        db_conn.close()
        return jsonify(data)

    except Exception as e:
        print(f"❌ Erreur SQL: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server is running on IP address: {local_ip}")

    # Confirming the IP address on the network
    if local_ip.startswith("127."):
        local_ip = os.popen("hostname -I").read().strip().split()[0]
    print(f"Server is accessible on network IP address: {local_ip}")
    app.run(host=local_ip , port=5001, debug=True, ssl_context=("cert.pem", "key.pem"))