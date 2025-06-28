import framework
import default_response as dr
import os

@framework.route("/", ["GET"])
def index(request : framework.Request):
	return framework.serve_file('htdocs/index.html')


framework.serve_forever()
