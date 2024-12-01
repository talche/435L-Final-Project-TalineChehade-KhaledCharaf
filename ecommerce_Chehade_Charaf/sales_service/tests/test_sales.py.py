from flask import Flask, request, jsonify
from flask_cors import CORS
from database import *  

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/customers', methods=['GET'])
def api_get_customers():
    return jsonify(get_customers())

@app.route('/api/customers/<username>', methods=['GET'])
def api_get_customer_by_username(username):
    return jsonify(get_customer_by_username(username))

@app.route('/api/customers/add', methods=['POST'])
def api_add_customer():
    customer = request.get_json()
    # Call insert_customer from the database
    inserted_customer = insert_customer(customer)
    if inserted_customer:
        return jsonify(inserted_customer), 201  # Return inserted customer data
    return jsonify({"error": "Customer could not be created"}), 400

# Route to update customer information
@app.route('/api/customers/update', methods=['PUT'])
def api_update_customer():
    customer = request.get_json()
    # Call update_customer from the database
    updated_customer = update_customer(customer)
    if 'error' in updated_customer:
        return jsonify(updated_customer), 400  # Return error if updating fails
    return jsonify(updated_customer), 200

# Route to delete a customer by username
@app.route('/api/customers/delete/<username>', methods=['DELETE'])
def api_delete_customer(username):
    # Call delete_customer from the database
    message = delete_customer(username)
    return jsonify(message), 200

# Route to charge a customer's account (add money to their wallet)
@app.route('/api/customers/charge/<username>', methods=['POST'])
def api_charge_account(username):
    data = request.get_json()
    amount = data.get("amount")
    if not amount:
        return jsonify({"error": "Amount is required"}), 400
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    # Call charge_account from the database
    result = charge_account(username, amount)
    return jsonify(result), 200

# Route to deduct money from a customer's wallet
@app.route('/api/customers/deduct/<username>', methods=['POST'])
def api_deduct_from_wallet(username):
    data = request.get_json()
    amount = data.get("amount")
    if not amount:
        return jsonify({"error": "Amount is required"}), 400
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    # Call deduct_from_wallet from the database
    result = deduct_from_wallet(username, amount)
    return jsonify(result), 200

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
