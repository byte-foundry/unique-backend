import os
import zipfile
import uuid
import smtplib
from pathlib import Path
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

import tornado.ioloop
import tornado.escape
import tornado.web
import tornado.httpclient

from weasyprint import HTML, CSS

from charge_customer import create_stripe_payment

coupon_url = os.environ["UNIQUE_COUPON_URL"]
http_client = tornado.httpclient.HTTPClient()
email_password = os.environ["UNIQUE_EMAIL_PASSWORD"]
email_login = os.environ["UNIQUE_EMAIL_LOGIN"]

def send_customer_email(zip_file, email, family_name):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email_login, email_password)

	msg = MIMEMultipart()
	msg['From'] = email_login
	msg['To'] = email
	msg['Subject'] = "Your unique font!"

	msg.attach(MIMEText('''Congratulations!

You just purchase your unique font.

I've taken the liberty to attach your package to this email.
If you signed up to Unique you'll be able to download your package later from your library.

Have a good one!''', 'plain'))
	file_to_attach = open(zip_file, "rb")

	attachment = MIMEBase("application", "octet-stream")
	attachment.set_payload(file_to_attach.read())
	encoders.encode_base64(attachment)
	attachment.add_header("Content-Disposition", "attachment", filename="unique_{0}.zip".format(family_name))

	msg.attach(attachment)

	server.sendmail(email_login, email, msg.as_string())

def create_zip(zip_name, zip_id, home, family, fonts):
	zip_to_send = zipfile.ZipFile(zip_name, mode="x", compression=zipfile.ZIP_DEFLATED)

	for font in fonts:
		font_file = open(home + "/.fonts/" + font["variant"] + "-" + zip_id + ".otf", "wb+");
		font_bytes = bytearray(font["data"])
		font_file.write(font_bytes)
		zip_to_send.writestr(family + " " + font["variant"] + ".otf", font_bytes)
		font_file.close()

	html = HTML(filename="specimen.html")
	css = CSS(string="* { font-family: " + family + ";}")
	pdf = html.write_pdf(stylesheets=[css])

	zip_to_send.writestr("specimen.pdf", pdf)
	zip_to_send.close()

def create_zip_and_send(zip_id, home, data):
		zip_name = "tmp/" + str(uuid.uuid4()) + ".zip"

		create_zip(zip_name, zip_id, home, data["family"], data["fonts"])

		binary_zip = open(zip_name, 'rb')

		if "email" in data:
			send_customer_email(zip_name, data["email"], data["family"])

		result = binary_zip.read()

		for font in data["fonts"]:
			os.remove(home + "/.fonts/" + font["variant"] + "-" + zip_id + ".otf");

		binary_zip.close()
		os.remove(zip_name);

		print("Package created")

		return result

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
		free = False

		if "coupon" in data:
			try:
				response = http_client.fetch(coupon_url + data["coupon"])
				coupon_data = tornado.escape.json_decode(response.body)
				percent_off = coupon_data["percentOff"]
				amount = int(amount - (amount * percent_off / 100))
				if percent_off == 100:
					free = True
			except tornado.httpclient.HTTPError as e:
				print(str(e))
			except Exception as e:
				print(str(e))

		if free:
			binary_zip = create_zip_and_send(str(uuid.uuid4()), home, data)
			self.write(binary_zip)
		else:
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
				binary_zip = create_zip_and_send(stripe_response.id, home, data)
				self.write(binary_zip)

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
