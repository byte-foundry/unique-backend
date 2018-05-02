import stripe
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback

stripe.api_key = os.environ["STRIPE_KEY"]
email_password = os.environ["UNIQUE_EMAIL_PASSWORD"]
email_login = os.environ["UNIQUE_EMAIL_LOGIN"]
admin_email = os.environ["UNIQUE_ADMIN_LOGIN"]

def send_error_msg_and_print(subject, e, email):
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email_login, email_password)

	error_msg = str(e)
	stacktrace = traceback.print_exception(type(e).__name__, e, None)

	msg = MIMEMultipart()
	msg['From'] = email_login
	msg['To'] = admin_email
	msg['Subject'] = subject

	msg.attach(MIMEText('''There is an error with unique server!
	user is:
	{0}
	error is:
	{1}
	stacktrace is:
	{2}'''.format(email, error_msg, stacktrace), 'plain'))

	server.sendmail(email_login, admin_email, msg.as_string())
	print(error_msg, stacktrace)


def create_stripe_payment(token, amount, currency, description, email, family):
	try:
		charge = stripe.Charge.create(
			amount=amount,
			currency=currency,
			source=token,
			description='Unique font "{0}"'.format(family)
		)
		if charge.status is "succeeded" or charge.paid:
			return charge
		else:
			return {"error": True, "reason": "Charge did not succeed"}
	except stripe.error.CardError as e:
		body = e.json_body
		err = body.get("error", {})
		print("Status is: {0}".format(err.http_status))
		print("Type is: {0}".format(err.get("type")))
		print("Code is: {0}".format(err.get("code")))
		print("Param is: {0}".format(err.get("param")))
		print("Message is: {0}".format(err.get("message")))
		return {"error": True, "reason": err.get("code")}
	except stripe.error.RateLimitError as e:
		print("Rate limit error")
		return {"error": True, "reason": "rate_limit"}
	except (
			stripe.error.InvalidRequestError,
			stripe.error.AuthenticationError,
			stripe.error.APIConnectionError,
			stripe.error.StripeError
	) as e:

		send_error_msg_and_print('There is a stripe error with unique server!', e, email)
		return {"error": True, "reason": 'stripe error'}
	except Exception as e:
		send_error_msg_and_print('There is a server error with unique server!', e, email)
		return {"error": True, "reason": 'server error'}

