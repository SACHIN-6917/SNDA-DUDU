# Razorpay Payment Integration Guide

## 💳 Complete Razorpay Setup for Industrial Visit Bookings

This guide covers the complete implementation of Razorpay payment gateway in DUDU Industrial Visit Management System.

---

## 📦 Step 1: Get Razorpay Credentials

### Create Razorpay Account

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Sign up with business email
3. Complete KYC (for production) or skip for testing

### Get API Keys

1. Navigate to **Settings** → **API Keys**
2. Generate Test Mode Keys:
   - **Key ID**: `rzp_test_xxxxxxxxxxxxxxxx`
   - **Key Secret**: `xxxxxxxxxxxxxxxxxxxxxx`
3. Click "Generate Test Key" to create new keys
4. Copy both Key ID and Secret

### Update .env

```bash
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_secret_key_here
RAZORPAY_ENABLED=True
```

---

## 🔧 Step 2: Backend Implementation (Already Done!)

The following files have been created/updated:

### ✅ `payment_utils.py`
- Razorpay client wrapper
- Order creation
- Payment verification
- Demo mode support

### ✅ `api_views.py`
- `PaymentCreateAPIView`: Creates Razorpay orders
- `PaymentVerifyAPIView`: Verifies payment signatures

### ✅ `urls.py`
- `/api/payment/create/` endpoint
- `/api/payment/verify/` endpoint

---

## 🎨 Step 3: Frontend Integration

### Update Payment Page HTML

Add Razorpay checkout script to `payment.html`:

```html
<!-- Add before closing </ body> tag -->
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

<script>
// Payment Integration
async function initiatePayment(bookingId, amount) {
    try {
        // Step 1: Create Razorpay order
        const createResponse = await fetch('/api/payment/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                booking_id: bookingId,
                amount: amount
            })
        });
        
        const orderData = await createResponse.json();
        
        if (orderData.status !== 'success') {
            throw new Error(orderData.message || 'Failed to create order');
        }
        
        // Step 2: Open Razorpay Checkout
        const options = {
            key: orderData.razorpay_key,
            amount: orderData.amount,
            currency: orderData.currency,
            order_id: orderData.order_id,
            name: 'DUDU IV Hub',
            description: 'Industrial Visit Booking Payment',
            image: '{% static "images/iv.png" %}',
            handler: async function(response) {
                // Step 3: Verify payment
                await verifyPayment(
                    bookingId,
                    response.razorpay_order_id,
                    response.razorpay_payment_id,
                    response.razorpay_signature
                );
            },
            prefill: {
                name: '{{ user.name }}',
                email: '{{ user.email }}',
                contact: '{{ user.phone }}'
            },
            theme: {
                color: '#e96718'
            },
            modal: {
                ondismiss: function() {
                    console.log('Payment cancelled by user');
                }
            }
        };
        
        const rzp = new Razorpay(options);
        rzp.open();
        
    } catch (error) {
        console.error('Payment initiation error:', error);
        showError('Failed to initiate payment: ' + error.message);
    }
}

async function verifyPayment(bookingId, orderId, paymentId, signature) {
    try {
        const verifyResponse = await fetch('/api/payment/verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                booking_id: bookingId,
                razorpay_order_id: orderId,
                razorpay_payment_id: paymentId,
                razorpay_signature: signature
            })
        });
        
        const result = await verifyResponse.json();
        
        if (result.status === 'success') {
            // Show success animation
            showSuccessAnimation();
            
            // Redirect after 2 seconds
            setTimeout(() => {
                window.location.href = '/account/?payment=success';
            }, 2000);
        } else {
            throw new Error(result.message || 'Payment verification failed');
        }
        
    } catch (error) {
        console.error('Payment verification error:', error);
        showError('Payment verification failed: ' + error.message);
    }
}

function showSuccessAnimation() {
    // Create success overlay
    const overlay = document.createElement('div');
    overlay.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                    background: rgba(0,0,0,0.8); z-index: 9999; display: flex; 
                    align-items: center; justify-content: center;">
            <div style="background: white; padding: 40px; border-radius: 20px; text-align: center;">
                <div class="checkmark-container">
                    <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52"
                         style="width: 80px; height: 80px; margin: 0 auto 20px;">
                        <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"
                                style="stroke: #4caf50; stroke-width: 2; stroke-dasharray: 166; 
                                       stroke-dashoffset: 166; animation: stroke 0.6s cubic-bezier(0.65,0,0.45,1) forwards;"/>
                        <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"
                              style="stroke: #4caf50; stroke-width: 3; stroke-dasharray: 48; 
                                     stroke-dashoffset: 48; animation: stroke 0.3s cubic-bezier(0.65,0,0.45,1) 0.8s forwards;"/>
                    </svg>
                </div>
                <h2 style="color: #4caf50; margin-bottom: 10px;">Payment Successful!</h2>
                <p style="color: #666;">Your booking has been confirmed.</p>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

function showError(message) {
    alert(message); // Replace with better UI notification
}

// Example: Attach to payment button
document.getElementById('paymentBtn')?.addEventListener('click', () => {
    const bookingId = document.getElementById('bookingId').value;
    const amount = document.getElementById('amount').value;
    initiatePayment(bookingId, amount);
});
</script>

<style>
@keyframes stroke {
    100% {
        stroke-dashoffset: 0;
    }
}
</style>
```

---

## 🧪 Step 4: Testing Payment Flow

### Test Card Details (Razorpay Test Mode)

Use these test cards for testing payments:

**Successful Payment:**
- Card Number: `4111 1111 1111 1111`
- CVV: Any 3 digits
- Expiry: Any future date
- Name: Any name

**Failed Payment:**
- Card Number: `4012 0010 3714 1112`
- CVV: Any 3 digits
- Expiry: Any future date

**UPI Test:**
- VPA: `success@razorpay`
- Enter any name

### Test Flow:

1. Navigate to booking page
2. Select an industrial visit
3. Click "Book Now"
4. Fill booking details
5. Click "Proceed to Payment"
6. Razorpay checkout opens
7. Enter test card details
8. Complete payment
9. See success animation
10. Verify booking status changed to "confirmed"

---

## 🔐 Step 5: Security Best Practices

### ✅ Server-Side Verification
- **Never trust client-side only**: Always verify payment signature on server
- **Use HTTPS in production**: All payment data must be encrypted
- **Store secrets securely**: Keep `RAZORPAY_KEY_SECRET` in .env, never commit

### ✅ Webhook Implementation (Recommended)

Add webhook endpoint for automatic payment notifications:

```python
# In views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import hmac
import hashlib

@csrf_exempt
def razorpay_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    # Verify webhook signature
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    webhook_signature = request.headers.get('X-Razorpay-Signature', '')
    webhook_body = request.body
    
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        webhook_body,
        hashlib.sha256
    ).hexdigest()
    
    if webhook_signature != expected_signature:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Process webhook event
    event_data = request.json()
    event_type = event_data.get('event')
    
    if event_type == 'payment.captured':
        payment_id = event_data['payload']['payment']['entity']['id']
        order_id = event_data['payload']['payment']['entity']['order_id']
        
        # Update booking status
        # ...
        
    return JsonResponse({'status': 'success'})
```

Add to URL conf:
```python
path('api/payment/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
```

Configure in Razorpay Dashboard:
1. Go to Settings → Webhooks
2. Add webhook URL: `https://yourdomain.com/api/payment/webhook/`
3. Select events: `payment.captured`, `payment.failed`
4. Generate webhook secret
5. Add to .env: `RAZORPAY_WEBHOOK_SECRET=your_webhook_secret`

---

## 📱 Step 6: Mobile Responsiveness

Ensure Razorpay checkout is mobile-friendly:

```css
/* In payment.css */
@media (max-width: 768px) {
    .razorpay-container {
        width: 100% !important;
        max-width: 100% !important;
    }
}
```

Razorpay's checkout is already mobile-optimized, but ensure your payment button is accessible on all devices.

---

## 🚀 Step 7: Production Deployment

### Before Going Live:

1. **Complete KYC**: Submit business documents to Razorpay
2. **Activate Live Mode**: Switch from test to live keys
3. **Update Credentials**:
   ```bash
   RAZORPAY_KEY_ID=rzp_live_your_live_key_id
   RAZORPAY_KEY_SECRET=your_live_secret_key
   ```
4. **Update Webhook URLs**: Use production domain
5. **Enable HTTPS**: SSL certificate mandatory for payments
6. **Test thoroughly**: Use small amount for initial live transaction
7. **Monitor**: Check Razorpay dashboard regularly

---

## 📊 Payment Flow Diagram

```
User selects package
       ↓
Fills booking form
       ↓
Clicks "Proceed to Payment"
       ↓
Frontend calls /api/payment/create/
       ↓
Backend creates Razorpay order
       ↓
Returns order_id to frontend
       ↓
Frontend opens Razorpay Checkout
       ↓
User enters payment details
       ↓
Razorpay processes payment
       ↓
Returns payment_id, signature
       ↓
Frontend calls /api/payment/verify/
       ↓
Backend verifies signature
       ↓
Updates booking status
       ↓
Shows success animation
       ↓
Redirects to account page
```

---

## 🐛 Troubleshooting

### Issue: "Key ID is required"
**Solution**: Ensure RAZORPAY_KEY_ID is set in .env and server is restarted

### Issue: "Signature verification failed"
**Solution**: Check that signature is sent correctly. Ensure webhook secret matches.

### Issue: "Amount mismatch"
**Solution**: Razorpay expects amount in paise (multiply rupees by 100)

### Issue: "Payment succeeded but booking not updated"
**Solution**: Check `/api/payment/verify/` endpoint logs. Ensure booking_id is correct.

---

## ✅ Implementation Checklist

- [ ] Razorpay account created
- [ ] Test API keys obtained
- [ ] .env file updated with keys
- [ ] `razorpay` package installed
- [ ] payment_utils.py created
- [ ] Payment APIs added to urls.py
- [ ] Frontend integration code added
- [ ] Test payment successful
- [ ] Success animation working
- [ ] Booking status updates correctly
- [ ] Webhook configured (optional)
- [ ] Mobile responsiveness tested
- [ ] Error handling implemented
- [ ] Ready for production

---

## 📞 Support Resources

- Razorpay Docs: https://razorpay.com/docs/
- Integration Guide: https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/
- API Reference: https://razorpay.com/docs/api/
- Python SDK: https://github.com/razorpay/razorpay-python
- Test Cards: https://razorpay.com/docs/payments/payments/test-card-details/

---

**Next Steps**: After payment integration, implement email notifications for successful bookings!
