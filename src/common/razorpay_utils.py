
import razorpay
from django.conf import settings

class RazorpayUtils:

    def __init__(self) -> None:
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        self.client.set_app_details({"title" : "Movie Bazaar", "version" : "1.0.0"})


    def create_order(self, original_amount:float, receipt:str, currency='INR'):

        '''
        response_sample: {'id': 'order_O9xdjdUdKgFU6R', 'entity': 'order', 'amount': 59900, 'amount_paid': 0, 'amount_due': 59900, 'currency': 'INR', 'receipt': None, 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1715599570}
        '''
 
        response = self.client.order.create(dict(
            amount=original_amount*100,
            currency=currency,
            receipt=receipt
        ))

        return response.get('id')
    
razorpay_client = RazorpayUtils()