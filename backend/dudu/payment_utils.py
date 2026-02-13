"""
Payment utilities for Razorpay integration
"""
import razorpay
from django.conf import settings
import hashlib
import hmac

class RazorpayClient:
    """
    Wrapper for Razorpay payment gateway operations
    """
    
    def __init__(self):
        self.client = None
        self.enabled = settings.RAZORPAY_ENABLED
        
        if self.enabled:
            try:
                self.client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
            except Exception as e:
                print(f"Razorpay initialization failed: {e}")
                self.enabled = False
    
    def create_order(self, amount, currency='INR', receipt=None, notes=None):
        """
        Create a Razorpay order
        
        Args:
            amount (int): Amount in smallest currency unit (paise for INR)
            currency (str): Currency code
            receipt (str): Receipt ID
            notes (dict): Additional notes
        
        Returns:
            dict: Order details or demo order if disabled
        """
        if not self.enabled or not self.client:
            # Return demo order for testing
            return {
                'id': 'order_demo_' + str(amount),
                'entity': 'order',
                'amount': amount,
                'currency': currency,
                'status': 'created',
                'receipt': receipt or 'demo_receipt',
                'notes': notes or {}
            }
        
        try:
            order_data = {
                'amount': int(amount * 100),  # Convert to paise
                'currency': currency,
                'receipt': receipt or f'receipt_{amount}',
            }
            
            if notes:
                order_data['notes'] = notes
            
            order = self.client.order.create(data=order_data)
            return order
        
        except Exception as e:
            print(f"Razorpay order creation failed: {e}")
            raise
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify Razorpay payment signature
        
        Args:
            razorpay_order_id (str): Order ID
            razorpay_payment_id (str): Payment ID
            razorpay_signature (str): Signature to verify
        
        Returns:
            bool: True if signature is valid
        """
        if not self.enabled:
            # In demo mode, always return True
            return True
        
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return True
        
        except razorpay.errors.SignatureVerificationError:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def fetch_payment(self, payment_id):
        """
        Fetch payment details
        
        Args:
            payment_id (str): Payment ID
        
        Returns:
            dict: Payment details
        """
        if not self.enabled or not self.client:
            return {
                'id': payment_id,
                'status': 'captured',
                'method': 'demo',
                'amount': 0
            }
        
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            print(f"Payment fetch failed: {e}")
            return None


# Singleton instance
razorpay_client = RazorpayClient()
