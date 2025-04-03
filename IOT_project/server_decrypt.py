import socket
import json
from datetime import datetime

HOST = "0.0.0.0"  # Nasłuchuj na wszystkich interfejsach
PORT = 5005       # Ten sam port co w ESP8266
key = 0x5A
BUFFER_SIZE = 1024

def xorDecrypt(encrypted_text, key):
    decrypted = bytearray(len(encrypted_text))
    for i in range(len(encrypted_text)):
        decrypted[i] = encrypted_text[i] ^ key [i % len(key)]
        return bytes(decrypted)

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

                    
                    encrypted_data = conn.recv(BUFFER_SIZE).decode().strip()
                        
                    decrypted_json = xorDecrypt(encrypted_data, key)
                    json = decrypted_json               

                    # Parsowanie JSON
                    json_data = json.loads(data.decode("utf-8"))
                    temperature = json_data["temperature"]
                    humidity = json_data["humidity"]
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Tworzenie wpisu logu
                    log = f"{timestamp} - Temperature: {temperature} °C, Humidity: {humidity} %"
                    print(log)

                    # Zapis do pliku
                    log_file.write(log + "\n")
                except json.JSONDecodeError:
                    print("JSON decoding error!")

