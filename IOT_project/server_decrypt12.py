from flask import Flask, request, jsonify
import jwt
import time

app = Flask(__name__)

# Tajny klucz, który jest używany do weryfikacji podpisu tokenu JWT
SECRET_KEY = 'my_secret_key'

# Funkcja do weryfikacji tokenu JWT
def verify_jwt(token):
    try:
        # Sprawdzanie ważności tokenu JWT
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token  # Zwraca dane z payload, jeśli token jest poprawny
    except jwt.ExpiredSignatureError:
        return None  # Token wygasł
    except jwt.InvalidTokenError:
        return None  # Nieprawidłowy token

# Endpoint do odbierania danych z ESP8266
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()  # Odbieranie danych JSON z ESP8266

    # Sprawdzanie, czy w danych jest token JWT
    if 'token' not in data:
        return jsonify({'error': 'Token missing'}), 400

    token = data['token']
    
    # Weryfikacja tokenu JWT
    decoded_token = verify_jwt(token)
    if decoded_token is None:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # Jeżeli token jest poprawny, przetwarzamy dane czujników
    temperature_dht = data.get('temperatureDHT')
    humidity = data.get('humidity')
    temperature_bmp = data.get('temperatureBMP')
    pressure = data.get('pressure')
    altitude = data.get('altitude')

    # Możesz teraz przetwarzać dane z czujników, np. zapisać do bazy danych
    print(f"Temperature DHT: {temperature_dht}")
    print(f"Humidity: {humidity}")
    print(f"Temperature BMP: {temperature_bmp}")
    print(f"Pressure: {pressure}")
    print(f"Altitude: {altitude}")

    # Odpowiedź serwera
    return jsonify({'message': 'Data received successfully!'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)  # Serwer nasłuchuje na porcie 5005
