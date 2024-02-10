import socket
import mysql.connector
from geopy.geocoders import Nominatim

PORT = 8080
SERVER = '172.20.86.122'
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "x"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(ADDR)
    print("Connected to the server")
except socket.error as e:
    print(f"Error: {e}")

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

def send(msg):
    client.send(msg.encode())

def receive():
    return client.recv(1024).decode()

def validate_user(user_id):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM User WHERE UserID = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                user_id, name, guardian_status, num_children, safety_status, location, *_ = user_data

                # Print the user details with clear labels
                print("User found. Details:")
                print(f"User ID: {user_id}")
                print(f"Name: {name}")
                print(f"Guardian Status: {'Guardian' if guardian_status else 'Non-Guardian'}")
                print(f"Number of Children: {num_children}")
                print(f"Safety Status: {safety_status}")
                print(f"Location: {location if location else 'Not provided'}")
            else:
                print("User not found.")
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
            cursor.execute("UPDATE User SET SafetyStatus = %s WHERE UserID = %s", (new_status, user_id))
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

def main_menu():
    while True:
        print("------------------------------------------")
        user_id = input("Enter UserID: ")
        send(user_id)
        response = receive()
        if response == "UserFound":
            print("User found. Details:")
            guardian_status = input("Are you a guardian? (yes/no): ")
            send(guardian_status)
            if guardian_status.lower() == "yes":
                print("1. Update status")
                print("2. Family status")
                print("3. Update location")
            else:
                print("1. Update status")
                print("2. Update location")
            choice = input("Enter your choice: ")
            send(choice)
            if choice == "1":
                new_status = input("Enter new status: ")
                send(new_status)
                update_status(user_id, new_status)
            elif choice == "2" and guardian_status.lower() == "yes":
                print("Family status functionality is not implemented.")
            elif choice == "3" or (choice == "2" and guardian_status.lower() != "yes"):
                new_location = input("Enter new location: ")
                send(new_location)
                update_location(user_id, new_location)
            else:
                print("Invalid choice.")
        elif response == "UserNotFound":
            print("User not found.")
        else:
            print("Unknown response from server.")

if __name__ == "__main__":
    main_menu()
