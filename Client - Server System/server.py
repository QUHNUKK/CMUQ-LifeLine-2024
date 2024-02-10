import socket
import threading
import mysql.connector
from geopy.geocoders import Nominatim

PORT = 8080
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '!Qwertz#z',
    'database': 'umeed'
}

def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")

    connected = True
    while connected:
        try:
            msg = conn.recv(1024).decode()  # Receive message from client
            if msg:
                print(f"[{addr}] {msg}")
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    process_message(conn, msg)
        except ConnectionResetError:
            print(f"[DISCONNECT] {addr} disconnected")
            connected = False

    conn.close()

def process_message(conn, msg):
    if msg.isdigit():  # Assume it's a user ID
        user_id = msg
        user_data = validate_user(user_id)
        if user_data:
            conn.send("UserFound".encode())
            guardian_status = conn.recv(1024).decode()
            if guardian_status.lower() == "yes":
                choice = conn.recv(1024).decode()
                if choice == "1":
                    new_status = conn.recv(1024).decode()
                    update_status(user_id, new_status)
                elif choice == "2":
                    print("Family status functionality is not implemented.")
                elif choice == "3":
                    new_location = conn.recv(1024).decode()
                    update_location(user_id, new_location)
                else:
                    print("Invalid choice.")
            else:
                choice = conn.recv(1024).decode()
                if choice == "1":
                    new_status = conn.recv(1024).decode()
                    update_status(user_id, new_status)
                elif choice == "2":
                    new_location = conn.recv(1024).decode()
                    update_location(user_id, new_location)
                else:
                    print("Invalid choice.")
        else:
            conn.send("UserNotFound".encode())
    else:
        print("Unknown message received.")

def validate_user(user_id):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM User WHERE UserID = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            connection.close()
            return user_data
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    return None

def update_status(user_id, new_status):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE User SET Status = %s WHERE UserID = %s", (new_status, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            print("Status updated successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def update_location(user_id, new_location):
    try:
        geolocator = Nominatim(user_agent="your_app_name")
        location = geolocator.geocode(new_location)
        if location:
            connection = connect_to_database()
            if connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE User SET Location = %s WHERE UserID = %s", (new_location, user_id))
                connection.commit()
                cursor.close()
                connection.close()
                print("Location updated successfully.")
        else:
            print("Invalid location.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def start():
    server.listen()
    print(f"[LISTENING] server is listening on {SERVER}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting")
start()
