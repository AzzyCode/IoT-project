from flask import Flask, render_template, jsonify, redirect, url_for, request
import pymysql
import hashlib
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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
app.secret_key = 'une_cle_secrete'  # Clé secrète nécessaire pour les sessions

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # Redirige vers la page de login si non authentifié

# Modèle utilisateur pour Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def get_id(self):
        return str(self.id)

# Fonction de chargement d'utilisateur requise par Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, password FROM users WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
            if user_data:
                return User(user_data['id'], user_data['name'], user_data['password'])
        except Exception as e:
            print(f"Erreur chargement utilisateur: {e}")
        finally:
            conn.close()
    return None

# Page de login (GET pour afficher le formulaire et POST pour authentifier)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_conn = get_db_connection()
        if not db_conn:
            return "Erreur de connexion à la base de données"

        try:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT id, name, password FROM users WHERE name = %s", (username,))
                user_data = cursor.fetchone()
            if user_data and hashlib.sha256(password.encode()).hexdigest() == user_data['password']:
                user = User(user_data['id'], user_data['name'], user_data['password'])
                login_user(user)
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="❌ Incorrect login, Please try again.")
        except Exception as e:
            print(f"❌ Erreur SQL: {e}")
            return f"Erreur SQL: {e}"
        finally:
            db_conn.close()
    else:
        return render_template('login.html')

# Déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))

# Page protégée index accessible uniquement par utilisateur authentifié
@app.route('/index')
@login_required
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
        return render_template("index.html", sensor_data=data)
    except Exception as e:
        print(f"❌ Erreur SQL: {e}")
        return f"Erreur SQL: {e}"
    finally:
        db_conn.close()

# Route signup (page d'inscription)
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/signupbis')
def signup_page_bis():
    return render_template('signupbis.html')

# Endpoint API protégé qui retourne les données des capteurs en JSON
@app.route("/sensor-data")
@login_required
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
        return jsonify(data)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        db_conn.close()

if __name__ == "__main__":
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Server is running on IP address: {local_ip}")

    # Confirming the IP address on the network
    if local_ip.startswith("127."):
        local_ip = os.popen("hostname -I").read().strip().split()[0]
    print(f"Server is accessible on network IP address: {local_ip}")
    app.run(host=local_ip , port=5001, debug=False, ssl_context=("cert.pem", "key.pem"))
