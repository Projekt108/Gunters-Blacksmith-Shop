
from flask import Flask, render_template, jsonify, session, redirect, url_for, request
import json
import os


# Sets up Flask application and secret key 
app = Flask(__name__)
PRICES = {'sword': 80.00, 'helm': 50.00, 'chestplate': 100.00, 'cooking-pot': 20.00, 'armored-boots': 40.00, 'healing-brew': 25.00, 'refined-saddle': 60.00, 'chalice': 15.00,
'chalice-saddle': 70.00, 'helmet-cooking-pot': 65.00, 'sword-potion': 90, 'full-set': 200.00 
}
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-change-me')

# Path to the JSON file for storing orders
DATA_FILE = os.path.join(app.root_path, 'data', 'orders.json')

COMMENTS_FILE = os.path.join(app.root_path, 'data', 'comments.json')
GAME_STATE_FILE = os.path.join(app.root_path, 'data', 'game_state.json')
INITIAL_GAME_STATE = {
    "cash": 0,
    "upgrades": 
    [
        {
            "id": 1, 
            "name": "River Panning", 
            "level": 0,
            "basecost": 10,
            "currentcost": 10,
            "money_generated": 4,
            "time": 2
        },
        {
            "id": 2, 
            "name": "Serfs", 
            "level": 0,
            "basecost": 50,
            "currentcost": 50,
            "money_generated": 20,
            "time": 5
        }
    ]
}

# Initialize comments file in case if it doesn't exist somehow
def initialize_comments():
    os.makedirs(os.path.dirname(COMMENTS_FILE), exist_ok=True)
    if not os.path.exists(COMMENTS_FILE) or os.stat(COMMENTS_FILE).st_size == 0:
        with open(COMMENTS_FILE, "w") as f:
            json.dump([], f)

# Initialize the orders file if it doesn't exist somehow
def initialize_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

# Initialize the game state file in case if it doesn't exist somehow
def initialize_game_state():
    os.makedirs(os.path.dirname(GAME_STATE_FILE), exist_ok=True)
    if not os.path.exists(GAME_STATE_FILE) or os.stat(GAME_STATE_FILE).st_size == 0:
        with open(GAME_STATE_FILE, "w") as f:
            json.dump(INITIAL_GAME_STATE, f)

# Load orders from the JSON file
def load_orders():
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, "r") as f:
        orders = json.load(f)

    if not isinstance(orders, list):
        raise ValueError("Orders data must be a JSON list")

    return orders

def load_game_state():
    if not os.path.exists(GAME_STATE_FILE):
        return INITIAL_GAME_STATE
    with open(GAME_STATE_FILE, "r") as f:
        game_state = json.load(f)
    return game_state

# All the routes for each page
# @app.route(url)
# def method(variable): 

# Home page route
@app.route('/') 
def home():    
    return render_template('index.html')

# Shop page route
@app.route('/shop')
def shop():
    return render_template('shop.html') 

# Queue page route
@app.route('/queue')
def queue():
    orders = load_orders()
    return render_template('queue.html', orders=orders)
# Game page route
@app.route('/game')
def game():
    game_state = load_game_state()
    return render_template('game.html', game_state=game_state)

@app.route('/get_game_state')
def get_game_state():
    state = load_game_state()
    return jsonify(state)

@app.route('/update_game_state', methods=['POST'])
def update_game_state():
    new_state = request.get_json()
    with open(GAME_STATE_FILE, "w") as f:
        json.dump(new_state, f)
    return jsonify({"status": True})


# About page route
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page route
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
# Buy page route, shows the page for the specific item
@app.route('/buy/<item_name>')
def buy_page(item_name):
    item_price = PRICES.get(item_name, 0.00)
    return render_template('buy.html', item_name=item_name, price=item_price)

# Add to cart route, gets the item name and quantity to put into the current cart
@app.route('/add_to_cart/<item_name>', methods=['POST'])
def add_to_cart(item_name):
    quantity = int(request.form.get('quantity') or 1)
    cart = session.get('cart', [])
    cart.append({"item_name": item_name, "quantity": quantity})
    session['cart'] = cart
    return redirect(url_for('view_cart'))

# Cart page route, with cart items and total price
@app.route('/cart')
def view_cart():
    cart_items = session.get('cart', [])
    # Calculate the total price
    total = sum(PRICES.get(item['item_name'], 0) * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, prices=PRICES, total=total)

@app.route('/clear_cart')
def clear_cart():
    # Clear the whole cart
    session.pop('cart', None)
    return redirect(url_for('shop'))

# Remove from cart route, removes an item from the current cart
@app.route('/remove_from_cart/<int:index>', methods=['POST'])
def remove_from_cart(index):
    # Retrieve the current cart from the session
    cart = session.get('cart', [])

    # Remove the item at the specified index if it exists
    if 0 <= index < len(cart):
        cart.pop(index)
        session['cart'] = cart

    return redirect(url_for('view_cart'))

# Checkout page route
@app.route('/checkout')
def checkout():
    # Check if the cart is empty before proceeding to checkout
    if not session.get('cart'):
        return redirect(url_for('view_cart'))

    return render_template('checkout.html')

# Submit order route, includes client name, status, and cart items  
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
        # Save the updated orders list to the data file
        with open(DATA_FILE, "w") as f:
            json.dump(orders_list, f, indent=4)
    # Handles errors
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
        if password == "staff@123": 
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
# Staff logout route
@app.route('/staff_logout')
def staff_logout():
    session.pop('is_staff', None)
    return redirect(url_for('staff'))

# Allows staff to advance the order to the next status 
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

# Allows staff to submit comments
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
            
    return redirect(url_for('contact', success = 1))
# Clears all orders from the list
@app.route('/clear_orders', methods=['POST'])
def clear_orders():
    if not session.get('is_staff'):
        return "Unauthorized no access for you", 403
        
    #Overwrite file with an empty list to clear it
    with open(DATA_FILE, "w") as f:
        json.dump([], f)
        
    return redirect(url_for('staff'))
# Clears all comments from the list
@app.route('/clear_comments', methods=['POST'])
def clear_comments():
    if not session.get('is_staff'):
        return "Unauthorized no access for you", 403
        
    #Overwrite file with an empty list to clear it
    with open(COMMENTS_FILE, "w") as f:
        json.dump([], f)
        
    return redirect(url_for('staff'))
# Removes a specific order from the list
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

# Initialize data and comments files if they do not exist already
initialize_file()
initialize_comments()
initialize_game_state()

# Run the web application
if __name__ == '__main__':
    app.run(port=3000, debug=True)
