import os
import zipfile
import uuid

import tornado.ioloop
import tornado.escape
import tornado.web

from weasyprint import HTML, CSS

from check_payment import check_stripe_payment

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Salut")

class PackageHandler(tornado.web.RequestHandler):
	def post(self):
		# Get stuff from request (fonts, receipt data, email)
		# Generate specimen from specimen.html and inject font face
		# Generate receipt
		# create zip with everything and send to email
		data = tornado.escape.json_decode(self.request.body)

		if check_stripe_payment(data["paymentNumber"]):
			zip_name = "tmp/" + str(uuid.uuid4()) + ".zip"
			zip_to_send = zipfile.ZipFile(zip_name, mode="x", compression=zipfile.ZIP_LZMA)

			for font in data["fonts"]:
				font_file = open("/home/franzp/.fonts/" + font["variant"] + "-" + data["customerId"] + ".otf", "wb+");
				font_bytes = bytearray(font["data"]["data"])
				font_file.write(font_bytes)
				zip_to_send.writestr(data["family"] + " " + font["variant"] + ".otf", font_bytes)
				font_file.close()

			choices = data["invoice"]["choices"]

			for choice in choices:
				if choice["name"] == "specimen":
					html = HTML(filename="specimen.html")
					css = CSS(string="* { font-family: " + data["family"] + "; font-weight: 100; font-style: italic;}")
					pdf = html.write_pdf(stylesheets=[css])
					zip_to_send.writestr("specimen.pdf", pdf)

			zip_to_send.close()

			binary_zip = open(zip_name, 'rb')

			self.write(binary_zip.read())
		else:
			self.write("nay")

		for font in data["fonts"]:
			os.remove("/home/franzp/.fonts/" + font["variant"] + "-" + data["customerId"] + ".otf");

def make_app():
	settings = {
			"debug": True,
			}
	return tornado.web.Application([
		(r"/", MainHandler),
		(r"/create-package/", PackageHandler),
		], **settings)


if __name__ == "__main__":
	app = make_app()
app.listen(8000)
tornado.ioloop.IOLoop.current().start()
