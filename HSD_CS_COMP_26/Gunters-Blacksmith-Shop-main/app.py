
from flask import Flask, render_template, jsonify, session, redirect, url_for, request
import json
import os

# Initialize the Flask application and configure the secret key for security 
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-change-me')

# Path to the JSON file for storing orders
DATA_FILE = os.path.join(app.root_path, 'data', 'orders.json')

COMMENTS_FILE = os.path.join(app.root_path, 'data', 'comments.json')

# Initialize comments file in case if it doesn't exist somehow
def initialize_comments():
    os.makedirs(os.path.dirname(COMMENTS_FILE), exist_ok=True)
    if not os.path.exists(COMMENTS_FILE) or os.stat(COMMENTS_FILE).st_size == 0:
        with open(COMMENTS_FILE, "w") as f:
            json.dump([], f)

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
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html') 

@app.route('/queue')
def queue():
    orders = load_orders()
    return render_template('queue.html', orders=orders)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
    
@app.route('/buy/<item_name>')
def buy_page(item_name):
    return render_template('buy.html', item_name=item_name)

@app.route('/add_to_cart/<item_name>', methods=['POST'])
def add_to_cart(item_name):
    # Retrieve the current cart from the session
    quantity = int(request.form.get('quantity') or 1)
    cart = session.get('cart', [])
    cart.append({"item_name": item_name, "quantity": quantity})
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
        "order": current_cart_items,
        "status": "Getting Materials"
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

#-----Staff functions-----#

@app.route('/staff', methods=['GET', 'POST'])
def staff():
    # If submit the password form
    if request.method == 'POST':
        password = request.form.get('password')
        # Hardcoded password (Not a good idea in practice but it's ok)
        if password == "guntermunter": 
            session['is_staff'] = True
            return redirect(url_for('staff'))
        else:
            return render_template('staff.html', error="Incorrect password!")

    # Check if already logged in
    if session.get('is_staff'):
        orders = load_orders()
        
        # Load comments
        try:
            with open(COMMENTS_FILE, "r") as f:
                comments = json.load(f)
        except:
            comments = []
            
        return render_template('staff.html', logged_in=True, orders=orders, comments=comments)
    
    # If not logged in show the password screen
    return render_template('staff.html', logged_in=False)

@app.route('/staff_logout')
def staff_logout():
    session.pop('is_staff', None)
    return redirect(url_for('staff'))

@app.route('/advance_order/<int:index>', methods=['POST'])
def advance_order(index):
    if not session.get('is_staff'):
        return "Unauthorized", 403
        
    orders = load_orders()
    if 0 <= index < len(orders):
        current_status = orders[index].get('status', 'Getting Materials')
        
        # Cycle through statuses
        if current_status == "Getting Materials":
            orders[index]['status'] = "Forging"
        elif current_status == "Forging":
            orders[index]['status'] = "Packing"
        elif current_status == "Packing":
            orders[index]['status'] = "Done"
            
        with open(DATA_FILE, "w") as f:
            json.dump(orders, f, indent=4)
            
    return redirect(url_for('staff'))

@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    comment_text = request.form.get('comment')
    if comment_text:
        try:
            with open(COMMENTS_FILE, "r") as f:
                comments = json.load(f)
        except:
            comments = []
            
        comments.append(comment_text)
        with open(COMMENTS_FILE, "w") as f:
            json.dump(comments, f, indent=4)
            
    return redirect(url_for('contact'))

@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if not session.get('is_staff'):
        return "Unauthorized no access for you", 403
        
    #Overwrite file with an empty list to clear it
    with open(DATA_FILE, "w") as f:
        json.dump([], f)
        
    return redirect(url_for('staff'))

@app.route('/delete_order/<int:index>', methods=['POST'])
def delete_order(index):
    if not session.get('is_staff'):
        return "Unauthorized", 403
        
    orders = load_orders()
    if 0 <= index < len(orders):
        orders.pop(index) #Remove the order at this position in the array
        
        with open(DATA_FILE, "w") as f:
            json.dump(orders, f, indent=4)
            
    return redirect(url_for('staff'))

initialize_file()
initialize_comments()

# Run the web application
if __name__ == '__main__':
    app.run(port=3000, debug=True)
