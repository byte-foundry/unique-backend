import stripe
import os

stripe.api_key = os.environ["STRIPE_KEY"]

def check_stripe_payment(payment_number):
    try:
        charge = stripe.Charge.retrieve(payment_number)
        if charge.paid:
            return True
        else:
            return False
    except:
        return False


