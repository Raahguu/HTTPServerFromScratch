ERRNO204 = """\
HTTP/1.1 204 No Content
Allow: {allowed_methods}
Access-Control-Allow_Methods: {allowed_methods}
""".replace("\n", "\r\n")

ERRNO400 = b"""\
HTTP/1.1 400 Bad Request
Content-type: test/plain
Content-length: 21

Error 400 Bad Request
""".replace(b"\n", b"\r\n")

ERRNO404 = b"""\
HTTP/1.1 403 Forbidden
Content-type: test/plain
Content-length: 19

Error 403 Forbidden
""".replace(b"\n", b"\r\n")

ERRNO404 = b"""\
HTTP/1.1 404 Not Found
Content-type: test/plain
Content-length: 24

Error 404 Page Not Found
""".replace(b"\n", b"\r\n")

ERRNO405 = b"""\
HTTP/1.1 405 Method Not Allowed
Content-type: text/plain
Content-length: 28

Error 405 Method Not Allowed
""".replace(b"\n", b"\r\n")


FILE_TEMPLATE = """\
HTTP/1.1 200 OK
Content-type: {content_type}
Content-length: {content_length}

""".replace("\n", "\r\n")

