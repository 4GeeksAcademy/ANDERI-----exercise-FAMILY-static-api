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

@app.route('/members', methods = ['GET'])
def handle_hello():
    # this is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = jsonify(members)
    return response_body, 200

@app.route("/member/<int:id>", methods=["GET"])
def handle_single_member(id):
    try:
        single_member = jackson_family.get_member(id)
        if single_member:
            return jsonify(single_member), 200
        else:
            return jsonify({"error": "Member not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/member/", methods=["POST"])
def add_new_member():
    try:
        new_member = request.json
        required_fields = ["first_name", "age", "lucky_numbers"]
        for field in required_fields:
            if field not in new_member:
                raise ValueError(f"Missing required field: {field}")

        jackson_family.add_member(new_member)
        members = jackson_family.get_all_members()
        response_body = jsonify(members)
        return response_body, 200

    except ValueError as ve:
        error_message = str(ve)
        return jsonify({"error": error_message}), 400

    except Exception as e:
        error_message = "An error occurred while adding a new member"
        return jsonify({"error": error_message}), 500


@app.route("/member/<int:id>", methods=["DELETE"])
def delete_a_member(id):
    try:
        member_to_delete = jackson_family.delete_member(id)
        if member_to_delete:
            return jsonify({"done": member_to_delete}), 200
        else:
            return jsonify({"not done": "member not found"})
    except Exception as e:
        error_message = "An error occurred while deleting the member"
        return jsonify({"error": error_message}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
