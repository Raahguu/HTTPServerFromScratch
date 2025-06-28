import socket
import default_response as dr
import os

file_content_types = {
	"html" : "text/html",
	"txt" : "text",
	"xml" : "text/xml",
	"js" : "text/js",
	"css" : "text/css"
}

serve_funcs = {}

def route(path : str, allowed_methods: list):
	global serve_funcs
	def decorator(func):
		for method in allowed_methods:
			key = f"{path}:{method.upper()}"
			serve_funcs[key] = func
		return func
	return decorator
	

class Request():
	method: str
	path: str
	version: str
	headers: list[str]
	body: dict

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
			
			# get when the headers becomes the body
			request.body = {}
			change_index = data.index('') if '' in data and len(data) >= 1 else -1
			if change_index == -1: request.headers = data[1:]
			else: 
				request.headers = data[1:change_index]
				for d in data[change_index + 1:]:
					for i in d.split('&'):
						j = i.split('=', 1)
						request.body[j[0]] = j[1].replace('+', ' ')
			return request
		except Exception as e:
			print(f"Failed to parse request: {e}")
			client_sock.sendall(dr.ERRNO400)
			return False
			
def serve_GET(sock: socket.socket, request: Request):
	if request.method != "GET":
		raise TypeError(f"serve_GET only works for GET not {request.method}")
	path = request.path
	if path == "/": path = "/index.html"
	# Throw an error, if the path could be malicious
	if ".." in path: 
		sock.sendall(dr.ERRNO400)
		return False
	
	# Make all the files they can access need to be in the 'htdocs' folder
	path = "htdocs" + path
	# If the path they specify does not have a file type in it, add html to the end
	if "." not in path: path += ".html"
	print(f"GET Request for {path}")
	try:
		with open(path, "rb") as file:
			stat = os.stat(path)
			headers = dr.FILE_TEMPLATE.format(content_type=file_content_types[path.split('.')[-1]], 
											 content_length=stat.st_size).encode('utf-8')
			content = file.read().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
			sock.sendall(headers + content + b"\r\n")
	except (FileNotFoundError, IsADirectoryError) as e:
		sock.sendall(dr.ERRNO404)
	except PermissionError:
		sock.sendall(dr.ERRNO403)

def serve_POST(sock: socket.socket, request: Request):
	if request.method != "POST":
		raise TypeError(f"serve_POST only works for POST not {request.method}")
	[print(f'{k} = {v}') for k, v in request.body.items()]
	header = dr.FILE_TEMPLATE.format(content_type="text", content_length=sum(map(len, request.body.keys())) + 2 * len(request.body.keys()))
	sock.sendall(header.encode('utf-8') + "\r\n".join(request.body).encode('utf-8') + b"\r\n")

def handle_request(client_sock: socket.socket):
	request = Request.from_socket(client_sock)
	if not request: return False
	# Validate Path
	if "/../" in request.path:
		client_sock.sendall(dr.ERRNO400)
	global serve_funcs
	key = request.path + ":" + request.method.upper()
	func = serve_funcs.get(key, None)

	print(key)

	if func == None:
		client_sock.sendall(dr.ERRNO404)
		return False
	client_sock.sendall(func(request))
		

def serve_forever(host = '127.0.0.1', port = 8080, max_request_line_length = 5):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Allow the server to run on an address alreayd used by another socket
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Bind the server to a port
	server.bind((host, port))
	# Now start the server
	server.listen(max_request_line_length)
	print(f"listening on {host}:{port}...")

	# Listening for connections
	while True:
		client_sock, client_addr = server.accept()
		handle_request(client_sock)
		client_sock.close() # Need to close so their browser page loads
	
if __name__ == "__main__":
	serve_forever()
