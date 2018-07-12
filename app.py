import os
import zipfile
import uuid
import smtplib
import time
import base64
from datetime import datetime
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
from email_html import get_html_email

coupon_url = os.environ["UNIQUE_COUPON_URL"]
http_client = tornado.httpclient.HTTPClient()
email_password = os.environ["UNIQUE_EMAIL_PASSWORD"]
email_login = os.environ["UNIQUE_EMAIL_LOGIN"]

if "PYTHON_ENV" in os.environ:
	upload_url = "https://tc1b6vq6o8.execute-api.eu-west-1.amazonaws.com/dev/unique/projects/{0}/uploads"
else:
	upload_url = "https://e4jpj60rk8.execute-api.eu-west-1.amazonaws.com/prod/unique/projects/{0}/uploads"

if "PYTHON_ENV" in os.environ:
	coupon_use_url = "https://tc1b6vq6o8.execute-api.eu-west-1.amazonaws.com/dev/webhooks/unique/couponRedeemed"
else:
	coupon_use_url = "https://e4jpj60rk8.execute-api.eu-west-1.amazonaws.com/prod/webhooks/unique/couponRedeemed"

def send_customer_email(zip_file, email, family_name):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email_login, email_password)

	msg = MIMEMultipart("alternative")
	msg['From'] = email_login
	msg['To'] = email
	msg['Subject'] = "Your unique font!"

	msg.attach(MIMEText('''Hi!
Yay, you made it, you’ve created a brand new font ready to use in all your projects! We’re so proud of you.
For your reference, we’ve attached your fonts in this email. You should receive the invoice in another email soon.

In case you’ll be back to create an account or visit your Unique font library, we will store your font and look after it for you.

Feel free to spread the word and tell your friends about us! :)

Eager to make your next font? Let’s go!''', 'plain'))
	msg.attach(MIMEText(get_html_email(), 'html'))
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

	#Add readme
	readme_file = open("README.txt", "r");
	zip_to_send.writestr("README.txt", readme_file.read())
	readme_file.close()

	html = HTML(filename="specimen.html")
	css = CSS(string=".cus-font { font-family: '" + family + "';}")
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
	os.remove(zip_name)

	now_date = datetime.now()

	if "email" in data:
		print("Package created for {0}".format(data["email"]))
	else:
		print("Package created with coupon 100%".format())

	return result

def upload_to_s3(bytes_to_upload, project_id):
	formatted_url = upload_url.format(project_id)
	base64_payload = base64.b64encode(bytes_to_upload)
	s3_request = tornado.httpclient.HTTPRequest(
			formatted_url,
			method="POST",
			body=base64_payload,
			headers={"Content-type": "application/json"}
			)
	now_date = datetime.now()
	print("Package uploaded with id {0}".format(project_id))
	response = http_client.fetch(s3_request)

def use_unique_coupon(coupon):
	coupon_request = tornado.httpclient.HTTPRequest(
			coupon_use_url,
			method="POST",
			body=tornado.escape.json_encode({
				"type": "charge.succeeded",
				"data": {
					"object": {
						"metadata": {
							"unique": "true",
							"coupon": coupon
							}
						}
					}
				}),
			headers={"Content-type": "application/json"}
			)
	now_date = datetime.now()
	print("Used coupon {0}".format(coupon))
	response = http_client.fetch(coupon_request)

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("Salut")

class PackageHandler(tornado.web.RequestHandler):
	def set_default_headers(self):
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
		coupon = False

		if "coupon" in data:
			coupon = data["coupon"]
			try:
				print(coupon_url + coupon)
				response = http_client.fetch(coupon_url + coupon)
				coupon_data = tornado.escape.json_decode(response.body)
				percent_off = coupon_data["percentOff"]
				amount = int(amount - (amount * percent_off / 100))
				if percent_off == 100:
					free = True
			except tornado.httpclient.HTTPError as e:
				print("HTTPError while retrieveng coupon" + str(e.response.body))
			except Exception as e:
				print("Unknown error while retrieveng coupon" + str(e))

		if free:
			binary_zip = create_zip_and_send(str(uuid.uuid4()), home, data)
			use_unique_coupon(coupon)
			self.write(binary_zip)
		else:
			now_date = datetime.now()
			print("Charging {0} for {1}{2}".format(data["email"], amount, data["currency"]))
			stripe_response = create_stripe_payment(
					data["source"],
					amount,
					data["currency"],
					data["description"],
					data["email"],
					data["family"],
					coupon
					)
			if "error" in stripe_response:
				print("Cannot package for payment " + data["paymentNumber"])
				self.set_status(401)
				self.set_header("Content-Type", "application/json");
				self.write({"error": {"reason": "payment failed"}})
			else:
				print("Charged succesfully {0} for {1}{2}".format(data["email"], amount, data["currency"]))
				binary_zip = create_zip_and_send(stripe_response.id, home, data)
				try:
					upload_to_s3(binary_zip, data["projectId"])
				except tornado.httpclient.HTTPError as e:
					print("HTTPError while while uploading to s3: " + str(e.response.body))
					self.set_status(e.code)
					self.set_header("Content-Type", "application/json");
					self.write(e.response.body)
					return
				except Exception as e:
					print("Unknown error while uploading to s3: " + str(e))
					self.set_status(500)
					self.write(str(e))
					return
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
	print("App Launched")
	app = make_app()

port = 8003

if "PYTHON_ENV" in os.environ:
	port = 8004

app.listen(port)
tornado.ioloop.IOLoop.current().start()
