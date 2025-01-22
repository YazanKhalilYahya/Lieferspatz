import sqlite3

# Initialize the database (create tables)
def init_db():
    conn = sqlite3.connect('lieferspatz.db')
    cursor = conn.cursor()

    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        street_name TEXT NOT NULL,
        house_number TEXT NOT NULL,
        city TEXT NOT NULL,
        zip_code TEXT NOT NULL,
        password TEXT NOT NULL,
        wallet_balance REAL DEFAULT 100.0
    );
    ''')

    # Create restaurants table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        street_name TEXT NOT NULL,
        house_number TEXT NOT NULL,
        city TEXT NOT NULL,
        zip_code TEXT NOT NULL,
        description TEXT,
        password TEXT NOT NULL,
        wallet_balance REAL DEFAULT 0.0
    );
    ''')

    # Create menu_items table with photo_url column for photos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        photo_url TEXT,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    );
    ''')

    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        restaurant_id INTEGER NOT NULL,
        status TEXT DEFAULT 'in Bearbeitung',
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    );
    ''')

    conn.commit()  # Commit changes to the database
    conn.close()   # Close the database connection

# Insert sample data into the database
def insert_data():
    conn = sqlite3.connect('lieferspatz.db')
    cursor = conn.cursor()

    # Insert sample customer
    cursor.execute('''
    INSERT INTO customers (first_name, last_name, street_name, house_number, city, zip_code, password)
    VALUES ('John', 'Doe', 'Hauptstr.', '123A', 'Berlin', '10115', 'password123');
    ''')

    # Insert sample restaurant
    cursor.execute('''
    INSERT INTO restaurants (name, street_name, house_number, city, zip_code, description, password)
    VALUES ('Restaurant A', 'Berliner Str.', '456', 'Hamburg', '20095', 'Delicious food!', 'restaurantpassword');
    ''')

    # Insert sample menu item with photo
    cursor.execute('''
    INSERT INTO menu_items (restaurant_id, name, description, price, photo_url)
    VALUES (1, 'Burger', 'A tasty burger', 5.99, 'https://example.com/burger.jpg');
    ''')

    conn.commit()  # Commit changes to the database
    conn.close()   # Close the database connection
