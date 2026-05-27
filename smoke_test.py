import requests
s = requests.Session()
base = 'http://127.0.0.1:5000'
login = s.post(base + '/login', data={'username': 'cashier', 'password': 'cashier123'}, allow_redirects=True)
print('login_status', login.status_code, 'final_url', login.url)
products = s.get(base + '/products', allow_redirects=True)
print('products_status', products.status_code, 'len', len(products.text), 'contains_admin_link', 'Add Product' in products.text)
