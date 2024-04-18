"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def handle_hello():
    # this is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = {
        "family": members
    }
    return jsonify(response_body), 200

@app.route('/members/<int:id>', methods=['GET'])
def handle_hello_member(id):
    member = jackson_family.get_member(id)
    try:
        if not member:
            raise APIException("Miembro no encontrado", status_code=400)
        return jsonify(member), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/member', methods=['POST'])
def add_new_member():
    try:
        member = request.json
        if member is None or not all(key in member for key in ["first_name", "last_name", "age", "lucky_numbers"]):
            raise ValueError("El objeto JSON de la solicitud está incompleto")
        jackson_family.add_member(member)
        return jsonify(jackson_family.get_all_members()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/member/<int:id>", methods=["DELETE"])
def delete_family_member(id):
    try:
        deleted_member = jackson_family.delete_member(id)
        if not deleted_member:
            raise APIException("Miembro no encontrado", status_code=400)
        return jsonify({"done": "Miembro eliminado"})
    except Exception as e:
        # Handle error 500
        return jsonify({"error": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
