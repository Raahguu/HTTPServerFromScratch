import socket
import default_response as dr

HOST = "127.0.0.1"
PORT = 80
MAX_REQUEST_LINE_LENGTH = 5

class Request():
	method: str
	path: str
	version: str
	headers: list[str]

	@classmethod
	def from_socket(cls, client_socket : socket.socket) -> 'Request':
		try:
			request_data = client_socket.recv(1024).decode('utf-8')
			data = [line for line in request_data.splitlines()]
			first_line = data[0].split()
			request = Request()
			request.method = first_line[0]
			request.path = first_line[1]
			request.version = first_line[2]
			request.headers = data[1:]
			return request
		except Exception as e:
			print(f"Failed to parse request: {e}")
			client_socket.sendall(dr.ERRNO400)
			

def handle_request(client_sock: socket.socket):
	request = Request.from_socket(client_sock)
	client_sock.sendall(dr.HELLO_WORLD)
	# Remember to close, or the client will wait forever
	client_sock.close()
		

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
	
if __name__ == "__main__":
	serve_forever()
