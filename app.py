from flask import Flask, render_template, jsonify, session, redirect, url_for, request
import json
import os

app = Flask(__name__)
app.secret_key = 'gunters_forge_secret'
DATA_FILE = os.path.join('data', 'orders.json')

def initialize_file():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

# Route to serve the main blacksmith shop page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the individual buy page
@app.route('/buy/<item_name>')
def buy_page(item_name):
    # Passes the name of the item to the HTML template so it knows what to display
    return render_template('buy.html', item_name=item_name)

# Route that handles adding the item to the cart, then sends you to the cart page
@app.route('/add_to_cart/<item_name>', methods=['POST'])
def add_to_cart(item_name):
    # If the user doesn't have a cart yet, create an empty one
    if 'cart' not in session:
        session['cart'] = []
    
    # Add the item to the cart and save it back to the session
    cart = session['cart']
    cart.append(item_name)
    session['cart'] = cart
    
    # Send the user to the cart page to see their updated cart
    return redirect(url_for('view_cart'))

# Route to view everything in the cart
@app.route('/cart')
def view_cart():
    # Grab the cart from the session, or an empty list if it doesn't exist
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)

# Read orders.json file
@app.route('/api/orders', methods=['GET'])
def get_orders():
    data_path = os.path.join('data', 'orders.json')
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            orders = json.load(f)
        return jsonify(orders)
    return jsonify([])

@app.route('/remove_from_cart/<int:index>', methods=['POST'])
def remove_from_cart(index):
    if 'cart' in session:
        cart = session['cart']
        # Check if the index is valid before popping it
        if 0 <= index < len(cart):
            cart.pop(index)
            session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    if not session.get('cart'):
        return redirect(url_for('view_cart'))
    return render_template('checkout.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    current_cart_items = session.get('cart', [])
    new_order = {"first_name": first_name, "last_name": last_name, "order": current_cart_items}

    session.pop('cart', None)

    orders_list = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                orders_list = json.load(f)
            except json.JSONDecodeError:
                orders_list = []

    orders_list.append(new_order)

    print("SAVING TO FILE PATH:", os.path.abspath(DATA_FILE))

    with open(DATA_FILE, "w") as f:
        json.dump(orders_list, f, indent=4)

    return render_template('order_success.html', first_name=first_name)


if __name__ == '__main__':
    app.run(port=3000, debug=True)