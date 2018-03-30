import os
import zipfile
import uuid
from pathlib import Path

import tornado.ioloop
import tornado.escape
import tornado.web

from weasyprint import HTML, CSS

from check_payment import check_stripe_payment

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Salut")

class PackageHandler(tornado.web.RequestHandler):
	def set_default_headers(self):
		print("setting headers for CORS")
		unique_origin = ["http://localhost:3000", "https://unique-beta.prototypo.io", "https://unique-dev.prototypo.io", "https://unique.prototypo.io"]
		origin = self.request.headers["origin"]
		if origin in unique_origin:
			self.set_header("Access-Control-Allow-Origin", origin)
			self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
			self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

	def options(self):
		self.set_status(204)
		self.finish()

	def post(self):
		# Get stuff from request (fonts, receipt data, email)
		# Generate specimen from specimen.html and inject font face
		# Generate receipt
		# create zip with everything and send to email
		data = tornado.escape.json_decode(self.request.body)
		home = str(Path.home())

		if check_stripe_payment(data["paymentNumber"]):
			zip_name = "tmp/" + str(uuid.uuid4()) + ".zip"
			zip_to_send = zipfile.ZipFile(zip_name, mode="x", compression=zipfile.ZIP_LZMA)

			for font in data["fonts"]:
				font_file = open(home + "/.fonts/" + font["variant"] + "-" + data["paymentNumber"] + ".otf", "wb+");
				font_bytes = bytearray(font["data"]["data"])
				font_file.write(font_bytes)
				zip_to_send.writestr(data["family"] + " " + font["variant"] + ".otf", font_bytes)
				font_file.close()

			html = HTML(filename="specimen.html")
			css = CSS(string="* { font-family: " + data["family"] + "; font-weight: 100; font-style: italic;}")
			pdf = html.write_pdf(stylesheets=[css])

			zip_to_send.writestr("specimen.pdf", pdf)
			zip_to_send.close()

			binary_zip = open(zip_name, 'rb')

			self.write(binary_zip.read())

			for font in data["fonts"]:
				os.remove(home + "/.fonts/" + font["variant"] + "-" + data["customerId"] + ".otf");

			os.remove(zip_name);
			print("Package created")
		else:
			print("Cannot package for payment " + data["paymentNumber"])
			self.set_status(401)
			self.set_header("Content-Type", "application/json");
			self.write({"error": {"reason": "payment failed"}})

def make_app():
	settings = {
			"debug": True,
			}
	return tornado.web.Application([
		(r"/", MainHandler),
		(r"/create-package/", PackageHandler),
		])


if __name__ == "__main__":
	app = make_app()
	print("App Launched")

app.listen(8003)
tornado.ioloop.IOLoop.current().start()
