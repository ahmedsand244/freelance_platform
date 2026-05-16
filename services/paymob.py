import requests
from django.conf import settings

class PaymobManager:
    """Class to handle Paymob standard integration flow without any external libraries"""
    
    BASE_URL = "https://accept.paymob.com/api"

    @classmethod
    def get_auth_token(cls):
        """
        Step 1: Authentication
        Retrieves the authentication token using the API Key.
        """
        url = f"{cls.BASE_URL}/auth/tokens"
        # .strip() to remove any invisible/newline spaces which causes 400 error
        payload = {"api_key": str(settings.PAYMOB_API_KEY).strip()}
        
        response = requests.post(url, json=payload)
        if not response.ok:
            raise Exception(f"Paymob Auth Token Error: {response.status_code} - {response.text}")
            
        return response.json().get('token')

    @classmethod
    def create_order(cls, auth_token, amount_cents, merchant_order_id, items=None):
        """
        Step 2: Order Registration
        Registers an order to Paymob and returns the Paymob order ID.
        """
        if items is None:
            items = []
            
        url = f"{cls.BASE_URL}/ecommerce/orders"
        payload = {
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": str(amount_cents),
            "currency": "EGP",
            "merchant_order_id": str(merchant_order_id),
            "items": items,
        }
        response = requests.post(url, json=payload)
        if not response.ok:
            raise Exception(f"Paymob Create Order Error: {response.status_code} - {response.text}")
        return response.json().get('id')

    @classmethod
    def get_payment_key(cls, auth_token, paymob_order_id, amount_cents, integration_id, billing_data):
        """
        Step 3: Get Payment Key
        Generates a payment token that will be used for the iframe or wallet URL.
        """
        url = f"{cls.BASE_URL}/acceptance/payment_keys"
        payload = {
            "auth_token": auth_token,
            "amount_cents": str(amount_cents),
            "expiration": 3600,
            "order_id": paymob_order_id,
            "billing_data": billing_data,
            "currency": "EGP",
            "integration_id": str(integration_id).strip()
        }
        response = requests.post(url, json=payload)
        if not response.ok:
            raise Exception(f"Paymob Payment Key Error: {response.status_code} - {response.text}")
        return response.json().get('token')

    @classmethod
    def generate_mobile_wallet_url(cls, payment_token, mobile_number):
        """
        Step 4 (Wallet): Proceed with Wallet Payment
        Sends a request to pay with a mobile wallet, returns the redirect URL for the user.
        """
        url = f"{cls.BASE_URL}/acceptance/payments/pay"
        payload = {
            "source": {
                "identifier": mobile_number,
                "subtype": "WALLET"
            },
            "payment_token": payment_token
        }
        response = requests.post(url, json=payload)
        if not response.ok:
            raise Exception(f"Paymob Wallet URL Error: {response.status_code} - {response.text}")
        
        redirect_url = response.json().get('redirect_url')
        if not redirect_url:
            raise Exception("No redirect_url found from Paymob wallet request.")
        return redirect_url

    @classmethod
    def get_iframe_url(cls, payment_token):
        """
        Step 4 (Card): Construct Iframe URL
        Returns the Iframe URL for card payments
        """
        iframe_id = str(settings.PAYMOB_IFRAME_ID).strip()
        return f"https://accept.paymob.com/api/acceptance/iframes/{iframe_id}?payment_token={payment_token}"
