ERRNO400 = b"""\
HTTP/1.1 400 Bad Request
Content-type: test/plain
Content-length: 21

Error 400 Bad Request""".replace(b"\n", b"\r\n")

ERRNO404 = b"""\
HTTP/1.1 404 Not Found
Content-type: test/plain
Content-length: 24

Error 404 Page Not Found""".replace(b"\n", b"\r\n")

HELLO_WORLD = b"""\
HTTP/1.1 200 OK

Hello, World!""".replace(b"\n", b"\r\n")
