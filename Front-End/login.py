from http.server import HTTPServer, BaseHTTPRequestHandler
import mysql.connector
from urllib.parse import urlparse, parse_qs

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '!Qwertz#z',
    'database': 'umeed'
}

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse the form data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        username = form_data['username'][0]
        password = form_data['password'][0]

        try:
            # Connect to the MySQL database
            connection = mysql.connector.connect(**db_config)

            # Execute the SQL query to check if user exists
            cursor = connection.cursor()
            cursor.execute("SELECT UserID FROM User WHERE UserID = %s AND Password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Login successful!')
            else:
                self.send_response(401)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid credentials')

        except mysql.connector.Error as error:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {error}".encode('utf-8'))
        finally:
            # Close the database connection
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Server running...')
    httpd.serve_forever()
