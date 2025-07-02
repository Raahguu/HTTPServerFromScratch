import socket
import default_response as dr
import os
from jinja2 import Environment, FileSystemLoader

file_content_types = {
	"html" : "text/html",
	"txt" : "text",
	"xml" : "text/xml",
	"js" : "text/js",
	"css" : "text/css"
}

serve_funcs = {}

env = None

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
	cookies: dict

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

			# Extract Cookies from header
			request.cookies = {}
			for i, header in enumerate(request.headers):
				if header.startswith("Cookie:"):
					for cookie in header[7:].split(";"):
						name = cookie.split("=", 1)[0].strip()
						value = cookie.split("=", 1)[1].strip()
						request.cookies[name] = value
					del request.headers[i]
			return request
		except Exception as e:
			print(f"Failed to parse request: {e}")
			client_sock.sendall(dr.ERRNO400)
			return False

			
def render_file(file_path : str, **data):
	try:
		global env
		template = env.get_template(file_path)
		content = template.render(data).encode('utf-8')
		headers = dr.FILE_TEMPLATE.format(content_type=file_content_types[file_path.split('.')[-1]], 
										 content_length=len(content)).encode('utf-8')
		return (headers + content + b"\r\n")
	except (FileNotFoundError, IsADirectoryError) as e:
		return dr.ERRNO404
	except PermissionError:
		return dr.ERRNO403


def serve_file(file_path : str):
	try:
		with open(file_path, "rb") as file:
			content = file.read().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
			headers = dr.FILE_TEMPLATE.format(content_type=file_content_types[file_path.split('.')[-1]], 
											 content_length=len(content)).encode('utf-8')
			return (headers + content + b"\r\n")
	except (FileNotFoundError, IsADirectoryError) as e:
		return dr.ERRNO404
	except PermissionError:
		return dr.ERRNO403


def handle_request(client_sock: socket.socket):
	request = Request.from_socket(client_sock)
	if not request: return False

	# Validate Path
	if "/../" in request.path:
		client_sock.sendall(dr.ERRNO400)

	global serve_funcs
	key = request.path + ":" + request.method.upper()
	print(key)
	func = serve_funcs.get(key, None)

	# If custom mapping
	if func != None:
		client_sock.sendall(func(request))
		return True

	match request.method.upper():
		case "HEAD":
			func = serve_funcs.get(request.path + ":" + "GET", None)
			if func != None:
				get_response = func(request).splitlines()
				empty_line_index = get_response.index(b'')
				head_response = b"\r\n".join(get_response[:empty_line_index])
				client_sock.sendall(head_response)
				return True
		
		case "GET":
			global env
			client_sock.sendall(serve_file(env.loader.searchpath[0] + request.path))
			return True
		
		case "OPTIONS":
			available_methods = ["OPTIONS"]
			if (serve_funcs.get(request.path + ":" + "GET", None) != None
				or os.path.exists(default_file_path + request.path)): 
				available_methods += ["GET", "HEAD"]
			for method in ["POST", "PUT", "PATCH", "DELETE", "TRACE", "CONNECT"]:
				if serve_funcs.get(request.path + ":" + method, None) != None:
					available_methods.append(method)
			response = dr.ERRNO204.format(allowed_methods=", ".join(available_methods))
			client_sock.sendall(response.encode('utf-8'))
			return True

	# Else throw a 405 Error
	client_sock.sendall(dr.ERRNO405)
	return False


def serve_forever(host : str = '127.0.0.1', port : int= 8080, 
				  max_request_line_length : int = 5, default_file_path : str = 'htdocs'):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Allow the server to run on an address alreayd used by another socket
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# Bind the server to a port
	server.bind((host, port))
	# Now start the server
	server.listen(max_request_line_length)
	print(f"listening on {host}:{port}...")

	global env
	env = Environment(loader=FileSystemLoader(default_file_path))

	# Listening for connections
	while True:
		client_sock, client_addr = server.accept()
		handle_request(client_sock)
		client_sock.close() # Need to close so their browser page loads
	

if __name__ == "__main__":
	serve_forever()
