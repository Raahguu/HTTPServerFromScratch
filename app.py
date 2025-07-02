import framework
import default_response as dr
import os

@framework.route("/", ["GET"])
def index(request : framework.Request):
	return framework.render_file('index.html', message=["1", 2, 3, 4, 5], cookies={"uid": 4, "noid": 2})

@framework.route("/", ["POST"])
def index_post(request : framework.Request):
	print(request.headers)
	if request.body.get("username", "") != "Raahguu":
		return index(request)
	return framework.render_file('me.html')

framework.serve_forever()
