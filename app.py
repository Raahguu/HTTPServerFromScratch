import framework
import default_response as dr
import os

@framework.route("/", ["GET"])
def index(request : framework.Request):
	with open('htdocs/index.html', "rb") as f:
		stat = os.stat('htdocs/index.html')
		headers = dr.FILE_TEMPLATE.format(content_type="text/html", content_length=stat.st_size).encode('utf-8')
		content = f.read().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
		return headers + content + b"\r\n"

framework.serve_forever()
