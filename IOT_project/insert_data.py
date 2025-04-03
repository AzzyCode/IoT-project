import mariadb
import re

db_config = {
        "host": "localhost",
        "user": "user",
        "password": "qwertyDB",
        "database": "data",
}

log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Temperatura: ([\d.]+) °C, Wilgotność: ([\d.]+) %")

try:
    conn = mariadb.connect(**db_config)
    cursor = conn.cursor()

    with open("logs.txt", "r") as file:
        for line in file:
            match = log_pattern.match(line)
            if match:
                datatime, temperature, humidity = match.groups()

                cursor.execute(
                        "INSERT INTO sensor_data (datetime, temperature, humidity VALUES (%s, %s, %s)",

    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted successfully")

except mariadb.Error as e:   
    print(f"Error connection MariaDB: {e})
