import os
import zipfile
import uuid
from pathlib import Path

import tornado.ioloop
import tornado.escape
import tornado.web
import tornado.httpclient

from weasyprint import HTML, CSS

from charge_customer import create_stripe_payment

coupon_url = os.environ["UNIQUE_COUPON_URL"]
http_client = tornado.httpclient.HTTPClient()

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
		amount = data["amount"]

		if "coupon" in data:
			try:
				response = http_client.fetch(coupon_url + data["coupon"])
				coupon_data = tornado.escape.json_decode(response.body)
				percent_off = coupon_data["percentOff"]
				amount = int(amount - (amount * percent_off / 100))
			except tornado.httpclient.HTTPError as e:
				print(str(e))
			except Exception as e:
				print(str(e))

		stripe_response = create_stripe_payment(
			data["source"],
			amount,
			data["currency"],
			data["description"],
			data["email"]
		)
		if "error" in stripe_response:
			print("Cannot package for payment " + data["paymentNumber"])
			self.set_status(401)
			self.set_header("Content-Type", "application/json");
			self.write({"error": {"reason": "payment failed"}})
		else:
			zip_name = "tmp/" + str(uuid.uuid4()) + ".zip"
			zip_to_send = zipfile.ZipFile(zip_name, mode="x", compression=zipfile.ZIP_DEFLATED)

			for font in data["fonts"]:
				font_file = open(home + "/.fonts/" + font["variant"] + "-" + stripe_response.id + ".otf", "wb+");
				font_bytes = bytearray(font["data"])
				font_file.write(font_bytes)
				zip_to_send.writestr(data["family"] + " " + font["variant"] + ".otf", font_bytes)
				font_file.close()

			html = HTML(filename="specimen.html")
			css = CSS(string="* { font-family: " + data["family"] + ";}")
			pdf = html.write_pdf(stylesheets=[css])

			zip_to_send.writestr("specimen.pdf", pdf)
			zip_to_send.close()

			binary_zip = open(zip_name, 'rb')

			self.write(binary_zip.read())

			for font in data["fonts"]:
				os.remove(home + "/.fonts/" + font["variant"] + "-" + stripe_response.id + ".otf");

			os.remove(zip_name);
			print("Package created")

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

port = 8003
if "PYTHON_ENV" in os.environ:
	print("App Launched")
	port = 8004
app.listen(port)
tornado.ioloop.IOLoop.current().start()
