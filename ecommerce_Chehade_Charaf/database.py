import sqlite3

# Function to connect to the database
def connect_to_db():
    # Modify this to connect to your actual SQLite database file
    return sqlite3.connect('database.db')

# Function to create the database tables
def create_db_tables():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY NOT NULL,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                address TEXT,
                gender TEXT,
                marital_status TEXT,
                wallet REAL DEFAULT 0.0
            )
        ''')
        conn.commit()
        print("Customer table created successfully")
    except Exception as e:
        print(f"Customer table creation failed - {e}")
    finally:
        conn.close()

# Function to insert a new customer
def insert_customer(customer):
    inserted_customer = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        # Check if the username already exists in the database
        cur.execute("SELECT id FROM customers WHERE username = ?", (customer['username'],))
        existing_customer = cur.fetchone()

        if existing_customer:
            raise ValueError(f"Username '{customer['username']}' is already taken")

        # Insert the new customer into the customers table
        cur.execute('''
            INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer['full_name'],
            customer['username'],
            customer['password'],  # Ensure you hash the password in production
            customer['age'],
            customer['address'],
            customer['gender'],
            customer['marital_status'],
            customer.get('wallet', 0.0)  # Default wallet value to 0.0 if not provided
        ))
        
        conn.commit()

        # Retrieve the customer data that was just inserted
        cur.execute("SELECT * FROM customers WHERE username = ?", (customer['username'],))
        inserted_customer = cur.fetchone()

    except sqlite3.IntegrityError as e:
        print(f"Database integrity error: {e}")
    except ValueError as ve:
        print(ve)  # For username already taken
    except Exception as e:
        print(f"Error inserting customer: {e}")
        conn.rollback()  # Ensure rollback on error
    finally:
        conn.close()

    return inserted_customer

# Get all customers
def get_customers():
    customers = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row  # To access columns by name
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers")  # Changed to 'customers' table
        rows = cur.fetchall()

        # Convert row objects to dictionaries
        for i in rows:
            customer = {
                "customer_id": i["id"],  # Changed to 'id' based on the customers table
                "full_name": i["full_name"],
                "username": i["username"],
                "password": i["password"],
                "age": i["age"],
                "address": i["address"],
                "gender": i["gender"],
                "marital_status": i["marital_status"],
                "wallet": i["wallet"]
            }
            customers.append(customer)
    except Exception as e:
        print(f"Error: {e}")
        customers = []
    return customers

# Get customer by Username
def get_customer_by_username(customer_username):
    customer = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers WHERE username = ?", (customer_username,))
        row = cur.fetchone()

        if row:
            customer = {
                "customer_id": row["id"],
                "full_name": row["full_name"],
                "username": row["username"],
                "password": row["password"],
                "age": row["age"],
                "address": row["address"],
                "gender": row["gender"],
                "marital_status": row["marital_status"],
                "wallet": row["wallet"]
            }
    except Exception as e:
        print(f"Error: {e}")
        customer = {}
    return customer

# Update customer information
def update_customer(customer):
    """
    Update a customer's information by their username.
    The customer dictionary can contain one or more fields to update.

    :param customer: A dictionary containing the customer's details to be updated.
    :return: A message indicating success or failure of the update.
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        # Check if the customer with the given username exists
        cur.execute("SELECT * FROM customers WHERE username = ?", (customer['username'],))
        existing_customer = cur.fetchone()

        if not existing_customer:
            return {"error": "Customer not found"}

        # Prepare the list of fields to update (exclude 'username' from updates as it's the identifier)
        update_fields = []
        update_values = []

        for key, value in customer.items():
            if key != 'username':  # Don't update the username directly
                update_fields.append(f"{key} = ?")
                update_values.append(value)

        # Check if there are fields to update
        if not update_fields:
            return {"error": "No fields to update"}

        # Update the customer in the database
        update_clause = ', '.join(update_fields)
        cur.execute(f"UPDATE customers SET {update_clause} WHERE username = ?", (*update_values, customer['username']))
        conn.commit()

        # Fetch the updated customer data
        updated_customer = get_customer_by_username(customer['username'])
        return {"message": "Customer updated successfully", "customer": updated_customer}

    except Exception as e:
        print(f"Error updating customer: {e}")
        conn.rollback()
        return {"error": "Database error"}
    
    finally:
        conn.close()



# Delete a customer by ID
def delete_customer(username):
    message = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM customers WHERE username = ?", (username,))
        conn.commit()

        message["status"] = "Customer deleted successfully"
    except Exception as e:
        conn.rollback()
        message["status"] = "Cannot delete customer"
        print(f"Error: {e}")
    finally:
        conn.close()

    return message


def charge_account(username, amount):
    """
    Charge a customer's account (add money to their wallet).
    
    :param username: The username of the customer.
    :param amount: The amount to charge (add) to the customer's wallet.
    :return: A message indicating success or failure of the charge.
    """
    if amount <= 0:
        return {"error": "Amount must be positive"}
    
    try:
        # Establish a connection to the database
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check if the customer exists
        cur.execute("SELECT * FROM customers WHERE username = ?", (username,))
        customer = cur.fetchone()

        if not customer:
            print(f"Customer with username '{username}' not found.")
            return {"error": "Customer not found"}

        # Log current wallet balance before charging
        print(f"Current wallet balance for {username}: {customer['wallet']}")

        # Update the customer's wallet by adding the charge amount
        new_balance = customer["wallet"] + amount
        cur.execute("UPDATE customers SET wallet = ? WHERE username = ?", (new_balance, username))
        conn.commit()

        # Log the new wallet balance after charging
        print(f"New wallet balance for {username}: {new_balance}")

        return {"message": f"Account charged by ${amount}. New balance: ${new_balance}"}

    except Exception as e:
        print(f"Error charging account: {e}")
        conn.rollback()
        return {"error": "Failed to charge the account"}
    
    finally:
        conn.close()



def deduct_from_wallet(username, amount):
    """
    Deduct money from the customer's wallet.

    :param username: The username of the customer.
    :param amount: The amount to deduct from the customer's wallet.
    :return: A message indicating success or failure of the deduction.
    """
    if amount <= 0:
        return {"error": "Amount must be positive"}
    
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check if the customer exists
        cur.execute("SELECT * FROM customers WHERE username = ?", (username,))
        customer = cur.fetchone()

        if not customer:
            return {"error": "Customer not found"}

        # Check if the customer has enough balance
        if customer["wallet"] < amount:
            return {"error": "Insufficient funds"}

        # Update the customer's wallet by deducting the amount
        new_balance = customer["wallet"] - amount
        cur.execute("UPDATE customers SET wallet = ? WHERE username = ?", (new_balance, username))
        conn.commit()
        print(f"New wallet balance for {username}: {new_balance}")

        return {"message": f"${amount} deducted from wallet. New balance: ${new_balance}"}

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return {"error": "Failed to deduct from the wallet"}
    finally:
        conn.close()


#run the code
connect_to_db()
create_db_tables()
