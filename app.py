from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import stripe
import paypalrestsdk

# ✅ Flask App Configuration
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# ✅ Stripe Configuration
stripe.api_key = "sk_test_your_secret_key"  # Replace with your secret key
STRIPE_PUBLIC_KEY = "pk_test_your_publishable_key"  # Replace with your publishable key
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "AfADGfk3TgP4RsfU2A0ad0A03peng_2zAAzNJpY1-Z55swha1AqGuBPVGfo_VOVXlVmHPtVqKjSWiNvi",
    "client_secret": "EBzC2Qqr3LSsdS-ph68JpbJZzJRt-uQBKFZDOKG95nL2UfgGTnhecgiFTf54RAMnXj5dHSmeDsIkXLcY"
})
# ✅ Gitter API Configuration
GITTER_TOKEN = "your_gitter_token_here"
GITTER_ROOM_ID = "your_room_id_here"  # Get room ID from Gitter API

# ✅ Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirects to login page if unauthorized

# ✅ Gitter Messaging Function
def send_message_to_gitter(message):
    """Function to send messages to Gitter chat."""
    url = f"https://api.gitter.im/v1/rooms/{GITTER_ROOM_ID}/chatMessages"
    headers = {"Authorization": f"Bearer {GITTER_TOKEN}", "Content-Type": "application/json"}
    data = {"text": message}

    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """Handles sending messages to Gitter from a form."""
    if request.method == 'POST':
        message = request.form['message']
        send_message_to_gitter(f"{current_user.username}: {message}")
        flash("Message sent to Gitter!", "success")
    return redirect(url_for('home'))

# ✅ User Class for Authentication
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# ✅ Sample User Database
users = {
    "user1": User(id=1, username="user1", password="password123")
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

# ✅ Sample Product List
products = [
     {"id": 1, "name": "Laptop", "price": 700, "image": "https://images.unsplash.com/photo-1522199755839-a2bacb67c546?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8bGVub3ZvJTIwbGFwdG9wfGVufDB8fDB8fHww"},
    {"id": 2, "name": "Smartphone", "price": 500, "image": "https://cdn.thewirecutter.com/wp-content/media/2024/05/smartphone-2048px-1013.jpg"},
    {"id": 3, "name": "Headphones", "price": 100, "image": "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/airpods-4-hero-select-202409_FMT_WHH?wid=752&hei=636&fmt=jpeg&qlt=90&.v=1725502960389"},
    {"id": 4, "name": "Mouse", "price": 50, "image": "https://m.media-amazon.com/images/I/61l33dfloaL._AC_UF1000,1000_QL80_.jpg"},
    {"id": 5, "name": "headset", "price": 105, "image":"https://assets2.razerzone.com/images/pnx.assets/eacc83c0643ed2da8c9e98968f8aa215/headset-landingpg-500x500-barracuda.jpg"},
    {"id": 6, "name": "Iphone 16", "price": 2000 , "image":"https://mobitez.in/wp-content/uploads/2024/10/Apple-Iphone-16-pro-Max-A.jpg"},
    {"id": 7, "name": "keyboard", "price": 250 , "image":"https://antesports.com/wp-content/uploads/2023/04/1_c5c6da47-29a5-434c-8b45-4303e1906886.png"},
    {"id": 8, "name": "charger", "price": 350 , "image":"https://imageio.forbes.com/specials-images/imageserve/1048621702/USB-cable-charger-for-a-smartphone/960x0.jpg?format=jpg&width=960"},
    {"id": 9, "name": "Iphone charger", "price": 1350 , "image":"https://cdn.mos.cms.futurecdn.net/ftfHXf5YR5sX7VsQLUnK9o.jpg"},
    {"id": 10, "name": "Iphone 15", "price": 990 , "image":"https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-finish-select-202309-6-1inch-blue?wid=2560&hei=1440&fmt=jpeg&qlt=95&.v=1692923777972"},
    {"id": 11, "name": "Usb", "price": 20 , "image":"https://cdn.pixabay.com/photo/2013/07/12/18/04/usb-stick-152909_1280.png"},
    {"id": 12, "name": "Redmi 12 5G", "price": 570 , "image":"https://www.trikart.com/media/cache/2500x0/catalog/product/r/e/redmi_12_5g_china_white-1_1706609231.webp"}
]


# ✅ Routes
@app.route('/')
def home():
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart=cart_items, total_price=total_price)

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', {})
    
    for product in products:
        if product["id"] == product_id:
            if str(product_id) in cart:
                cart[str(product_id)]['quantity'] += 1
            else:
                cart[str(product_id)] = {"name": product["name"], "price": product["price"], "quantity": 1}
    
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
    
    session['cart'] = cart
    return redirect(url_for('cart'))

# ✅ Checkout Routes
@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    if not cart:
        flash("Your cart is empty. Add items before proceeding to checkout.", "warning")
        return redirect(url_for('home'))

    return render_template(
        'checkout.html',
        stripe_public_key=STRIPE_PUBLIC_KEY,
        total_price=total_price,
        cart=cart
    )

# ✅ Stripe Payment Route
@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    cart = session.get('cart', {})
    line_items = []

    for item_id, item in cart.items():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': item['name']},
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': item['quantity'],
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('checkout', _external=True)
        )

        return jsonify({'id': checkout_session.id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Stripe Success Route
@app.route('/success')
@login_required
def success():
    session.pop('cart', None)
    flash("Payment successful!", "success")
    return redirect(url_for('home'))

# ✅ PayPal Payment Route
@app.route('/create-paypal-payment', methods=['POST'])
@login_required
def create_paypal_payment():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('paypal_success', _external=True),
            "cancel_url": url_for('paypal_cancel', _external=True)
        },
        "transactions": [{
            "item_list": {
                "items": [
                    {
                        "name": item['name'],
                        "sku": str(item_id),
                        "price": f"{item['price']:.2f}",
                        "currency": "USD",
                        "quantity": item['quantity']
                    }
                    for item_id, item in cart.items()
                ]
            },
            "amount": {
                "total": f"{total_price:.2f}",
                "currency": "USD"
            }
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        flash("Error creating PayPal payment.", "danger")
        return redirect(url_for('cart'))

@app.route('/paypal-success')
@login_required
def paypal_success():
    session.pop('cart', None)
    flash("PayPal Payment successful!", "success")
    return redirect(url_for('home'))

@app.route('/paypal-cancel')
@login_required
def paypal_cancel():
    flash("PayPal Payment cancelled.", "warning")
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)
