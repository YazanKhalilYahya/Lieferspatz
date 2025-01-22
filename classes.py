class Customer:
    def __init__(self, first_name, last_name, address, zip_code, password):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.zip_code = zip_code
        self.password = password
        self.id = len(customers) + 1  # Auto-generate customer ID
        self.orders = []  # List of orders placed by the customer
        self.wallet_balance = 100  # Starting wallet balance for each customer

    def deduct_balance(self, amount):
        """ Deduct the amount from the customer's wallet """
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            return True
        return False

    def add_balance(self, amount):
        """ Add amount to the customer's wallet """
        self.wallet_balance += amount


class Restaurant:
    def __init__(self, name, address, description, password):
        self.name = name
        self.address = address
        self.description = description
        self.password = password
        self.menu = []  # A list to store menu items
        self.orders = []  # A list to store orders
        self.opening_hours = {}  # {day: (open_time, close_time)}
        self.delivery_radius = []  # List of zip codes
        self.id = len(restaurants) + 1  # Auto-generate restaurant ID
        self.wallet_balance = 0  # Restaurant's initial balance

    def add_balance(self, amount):
        """ Add amount to restaurant's balance """
        self.wallet_balance += amount


class MenuItem:
    def __init__(self, name, description, price, image=None):
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.id = len(menu_items) + 1  # Auto-generate menu item ID


class Order:
    def __init__(self, customer_id, restaurant_id, items, status='in Bearbeitung'):
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.items = items  # list of items with quantity
        self.status = status  # 'in Bearbeitung', 'in Zubereitung', 'storniert', 'abgeschlossen'
        self.timestamp = datetime.now()

    def total_price(self):
        """ Calculate the total price for the order """
        return sum(item['price'] * item['quantity'] for item in self.items)

    def process_payment(self):
        """ Process payment from the customer """
        total = self.total_price()
        lieferspatz_share = total * 0.15  # 15% for Lieferspatz
        restaurant_share = total * 0.85  # 85% for the restaurant

        customer = customers[self.customer_id]
        if not customer.deduct_balance(total):
            return False  # Not enough funds in the wallet

        # Add to the restaurant's balance
        restaurant = restaurants[self.restaurant_id]
        restaurant.add_balance(restaurant_share)

        # Add to Lieferspatz balance (if needed)
        global lieferspatz_balance
        lieferspatz_balance += lieferspatz_share

        return True
