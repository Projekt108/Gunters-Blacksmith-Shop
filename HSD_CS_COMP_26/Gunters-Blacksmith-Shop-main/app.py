
from flask import Flask, render_template, jsonify, session, redirect, url_for, request
import json
import os

# Initialize the Flask application and configure the secret key for security 
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-change-me')

# Path to the JSON file for storing orders
DATA_FILE = os.path.join(app.root_path, 'data', 'orders.json')

# Initialize the orders file if it doesn't exist
def initialize_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

# Load orders from the JSON file
def load_orders():
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, "r") as f:
        orders = json.load(f)

    if not isinstance(orders, list):
        raise ValueError("Orders data must be a JSON list")

    return orders

# Define the routes for the web application
# @app.route(url)
# def method(variable): 
@app.route('/') 
def home():
    orders = load_orders()
    return render_template('index.html', orders=orders)

@app.route('/buy/<item_name>')
def buy_page(item_name):
    return render_template('buy.html', item_name=item_name)

@app.route('/add_to_cart/<item_name>', methods=['POST'])
def add_to_cart(item_name):
    # Retrieve the current cart from the session
    cart = session.get('cart', [])
    cart.append(item_name)
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    # Retrieve the current cart items from the session
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)

@app.route('/api/orders', methods=['GET'])
def get_orders():
    # Attempt to load and return the orders as JSON
    try:
        return jsonify(load_orders())
    except (json.JSONDecodeError, ValueError):
        return jsonify({"error": "Invalid orders data"}), 500
    except OSError:
        return jsonify({"error": "Unable to read orders"}), 500

@app.route('/remove_from_cart/<int:index>', methods=['POST'])
def remove_from_cart(index):
    # Retrieve the current cart from the session
    cart = session.get('cart', [])

    # Remove the item at the specified index if it exists
    if 0 <= index < len(cart):
        cart.pop(index)
        session['cart'] = cart

    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    # Check if the cart is empty before proceeding to checkout
    if not session.get('cart'):
        return redirect(url_for('view_cart'))

    return render_template('checkout.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    first_name = (request.form.get('first_name') or '').strip()
    last_name = (request.form.get('last_name') or '').strip()
    current_cart_items = session.get('cart', [])
    # Validate the input and current cart items
    if not first_name or not last_name:
        return "First and last name are required.", 400
    if not current_cart_items:
        return redirect(url_for('view_cart'))
    # Create a new order dictionary with the validated data
    new_order = {
        "first_name": first_name,
        "last_name": last_name,
        "order": current_cart_items
    }

    try:
        orders_list = load_orders()
        orders_list.append(new_order)

        with open(DATA_FILE, "w") as f:
            json.dump(orders_list, f, indent=4)

    except (json.JSONDecodeError, ValueError):
        return "The orders file contains invalid data.", 500
    except OSError:
        return "Unable to save the order. Please try again.", 500

    # Clear the cart from the session after successfully submitting the order
    session.pop('cart', None)

    return render_template('order_success.html', first_name=first_name)

initialize_file()

# Run the web application
if __name__ == '__main__':
    app.run(port=3000, debug=True)
