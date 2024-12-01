from flask import Flask, request, jsonify
from flask_cors import CORS
from database import *  

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/inventory', methods=['GET'])
def api_get_inventory():
    return jsonify(get_inventory())

@app.route('/api/inventory/add', methods=['POST'])
def api_add_good():
    good = request.get_json()
    inserted_good = insert_good(good)
    if inserted_good:
        return jsonify(inserted_good), 201  
    return jsonify({"error": "Good could not be created"}), 400

@app.route('/api/inventory/update', methods=['PUT'])
def api_update_good():
    good = request.get_json()
    updated_good = update_good(good)
    if 'error' in updated_good:
        return jsonify(updated_good), 400  # Return error if updating fails
    return jsonify(updated_good), 200


@app.route('/api/inventory/deduct/<good_name>', methods=['POST'])
def api_deduct_goods(good_name):
    data = request.get_json()
    quantity = data.get("quantity")
    if not quantity:
        return jsonify({"error": "Quantity is required"}), 400
    if quantity <= 0:
        return jsonify({"error": "Quantity must be positive"}), 400
    # Call deduct_from_wallet from the database
    result = deduct_goods(good_name, quantity)
    return jsonify(result), 200

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)