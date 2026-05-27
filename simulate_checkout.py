import requests
s = requests.Session()
base = 'http://127.0.0.1:5000'
# Login
r = s.post(base + '/login', data={'username':'cashier','password':'cashier123'}, allow_redirects=True)
print('login', r.status_code, '->', r.url)
# Add product 1 to cart
r = s.post(base + '/cart/add/1', data={'quantity':'1'}, allow_redirects=True)
print('add', r.status_code, '->', r.url)
# Checkout
r = s.post(base + '/checkout', data={'customer_name':'Test User','customer_email':'test@example.com','discount':'0','payment_method':'Card'}, allow_redirects=True)
print('checkout', r.status_code, '->', r.url)
if '/order/' in r.url:
    print('Order created, order page length', len(r.text))
else:
    print('Checkout did not complete; final page:', r.url)
