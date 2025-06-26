import socket
import default_response as dr
import os

HOST = "127.0.0.1"
PORT = 8080
MAX_REQUEST_LINE_LENGTH = 5

class Request():
	method: str
	path: str
	version: str
	headers: list[str]

	@classmethod
	def from_socket(cls, client_sock: socket.socket) -> 'Request':
		try:
			request_data = client_sock.recv(1024).decode('utf-8')
			data = [line for line in request_data.splitlines()]
			first_line = data[0].split(' ')
			request = Request()
			request.method = first_line[0]
			request.path = first_line[1]
			request.version = first_line[2]
			request.headers = data[1:]
			return request
		except Exception as e:
			print(f"Failed to parse request: {e}")
			client_sock.sendall(dr.ERRNO400)
			
def serve_GET(sock: socket.socket, request: Request):
	if request.method != "GET": 
		raise TypeError(f"serve_GET only handles GET requests, not {request.method} requests")
	path = request.path
	if path == "/": path = "/index.html"
	# Throw an error, if the path could be malicious
	if ".." in path: 
		sock.sendall(dr.ERRNO400)
		return False
	
	# Make all the files they can access need to be in the 'content' folder
	path = "content" + path
	# If the path they specify does not have a file type in it, add html to the end
	if "." not in path: path += ".html"
	try:
		with open(path, "rb") as file:
			stat = os.stat(path)
			headers = dr.FILE_TEMPLATE.format(content_type="text/html", 
											 content_length=stat.st_size).encode('utf-8')
			sock.sendall(headers)
			sock.sendfile(file)
	except (FileNotFoundError, IsADirectoryError) as e:
		print(e)
		sock.sendall(dr.ERRNO404)
	except PermissionError:
		sock.sendall(dr.ERRNO403)


def handle_request(client_sock: socket.socket):
	request = Request.from_socket(client_sock)
	# Only GET is implemented yet
	if request.method != "GET":
		client_sock.sendall(dr.ERRNO405)
		return False
	serve_GET(client_sock, request)
		

def serve_forever():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Allow the server to run on an address alreayd used by another socket
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Bind the server to a port
	server.bind((HOST, PORT))
	# Now start the server
	server.listen(MAX_REQUEST_LINE_LENGTH)
	print(f"listening on {HOST}:{PORT}...")

	# Listening for connections
	while True:
		client_sock, client_addr = server.accept()
		handle_request(client_sock)
		client_sock.close() # Need to close so their browser page loads
	
if __name__ == "__main__":
	serve_forever()
