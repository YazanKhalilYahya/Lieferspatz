from flask import Flask, request, jsonify
from datetime import datetime
from classes import Customer, Restaurant, MenuItem, Order
from db import init_db, insert_data  # Import the functions from db.py


app = Flask(__name__)

# Initialize the database and insert sample data when the app starts
init_db()
#insert_data()

# In-memory storage (replace with real DB in production)
restaurants = {}
customers = {}
orders = []
menu_items = {}
notifications = []
lieferspatz_balance = 0  # Global balance for Lieferspatz


# Create a new customer account (register)
@app.route('/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    zip_code = data['zip_code']
    password = data['password']

    # Create new customer and save it
    customer = Customer(first_name, last_name, address, zip_code, password)
    customers[customer.id] = customer

    return jsonify({'success': True, 'customer_id': customer.id})


# Customer Login (authenticate)
@app.route('/customer/login', methods=['POST'])
def login_customer():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    password = data['password']

    # Find the customer by name and validate password
    for customer in customers.values():
        if customer.first_name == first_name and customer.last_name == last_name and customer.password == password:
            return jsonify({'success': True, 'customer_id': customer.id})

    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


# Create a new restaurant account
@app.route('/restaurant', methods=['POST'])
def create_restaurant():
    data = request.get_json()
    name = data['name']
    address = data['address']
    description = data['description']
    password = data['password']

    # Create new restaurant and save it
    restaurant = Restaurant(name, address, description, password)
    restaurants[restaurant.id] = restaurant

    return jsonify({'success': True, 'restaurant_id': restaurant.id})


# Add an item to the restaurant's menu
@app.route('/restaurant/<int:restaurant_id>/menu', methods=['POST'])
def add_menu_item(restaurant_id):
    data = request.get_json()
    name = data['name']
    description = data['description']
    price = data['price']
    image = data.get('image', None)

    restaurant = restaurants.get(restaurant_id)
    if not restaurant:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

    menu_item = MenuItem(name, description, price, image)
    restaurant.menu.append(menu_item)
    menu_items[menu_item.id] = menu_item

    return jsonify({'success': True, 'item_id': menu_item.id})


# Create a new order (from a customer)
@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_id = data['customer_id']
    restaurant_id = data['restaurant_id']
    items = data['items']  # List of items with quantity

    customer = customers.get(customer_id)
    restaurant = restaurants.get(restaurant_id)

    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    if not restaurant:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

    # Create the order with status 'in Bearbeitung'
    order = Order(customer_id, restaurant_id, items)
    customer.orders.append(order)
    restaurant.orders.append(order)
    orders.append(order)

    # Process the payment for the order
    if not order.process_payment():
        return jsonify({'success': False, 'message': 'Insufficient balance to complete the payment.'}), 400

    return jsonify({'success': True, 'order_id': len(orders)})


# Update the status of an order (for restaurant)
@app.route('/restaurant/<int:restaurant_id>/order/<int:order_id>/status', methods=['PUT'])
def update_order_status(restaurant_id, order_id):
    restaurant = restaurants.get(restaurant_id)

    if not restaurant:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

    # Find the order by order_id
    order = None
    for o in restaurant.orders:
        if o.id == order_id:
            order = o
            break

    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    data = request.get_json()
    new_status = data.get('status')

    # Check if the new status is valid
    valid_statuses = ['in Bearbeitung', 'in Zubereitung', 'storniert', 'abgeschlossen']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    # Update the order status
    order.status = new_status

    # Notify customer of the status change (example: simple print or logging in real app)
    return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})


# View a customer's order history
@app.route('/customer/<int:customer_id>/orders', methods=['GET'])
def view_order_history(customer_id):
    customer = customers.get(customer_id)

    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404

    # Sort orders by status (pending first)
    sorted_orders = sorted(customer.orders, key=lambda x: (x.status != 'in Bearbeitung', x.timestamp))

    order_details = []
    for order in sorted_orders:
        order_details.append({
            'order_id': len(order_details) + 1,
            'restaurant_name': restaurants[order.restaurant_id].name,
            'items': order.items,
            'total_price': order.total_price(),
            'status': order.status,
            'timestamp': order.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'orders': order_details})


# Get the status of a specific order (customer's view)
@app.route('/customer/<int:customer_id>/order/<int:order_id>', methods=['GET'])
def get_order_status(customer_id, order_id):
    customer = customers.get(customer_id)

    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404

    order = customer.orders[order_id - 1]  # 1-based order ID

    return jsonify({
        'order_id': order_id,
        'status': order.status,
        'restaurant_name': restaurants[order.restaurant_id].name,
        'items': order.items,
        'total_price': order.total_price(),
        'timestamp': order.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    })


# Get customer's wallet balance
@app.route('/customer/<int:customer_id>/wallet', methods=['GET'])
def get_wallet_balance(customer_id):
    customer = customers.get(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404

    return jsonify({'wallet_balance': customer.wallet_balance})


# Get restaurant's wallet balance
@app.route('/restaurant/<int:restaurant_id>/wallet', methods=['GET'])
def get_restaurant_wallet_balance(restaurant_id):
    restaurant = restaurants.get(restaurant_id)
    if not restaurant:
        return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

    return jsonify({'wallet_balance': restaurant.wallet_balance})


# Get global Lieferspatz wallet balance
@app.route('/lieferspatz/wallet', methods=['GET'])
def get_lieferspatz_wallet_balance():
    return jsonify({'lieferspatz_wallet_balance': lieferspatz_balance})


if __name__ == '__main__':
    app.run(debug=True)
