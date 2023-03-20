from model import *

from flask import Flask
from flask import jsonify
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

basic_auth = HTTPBasicAuth()


@basic_auth.verify_password
def verify_password(username, password):
    if password == "BestNonencryptedPasswordEver!!!":
        return username
    else:
        return None


@basic_auth.error_handler
def basic_auth_error(status):
    return jsonify({"success": False, "message": "Wrong credentials!"}), status


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"success": False, "message": "Object not found!"}), 404


@app.errorhandler(500)
def internal_error(error):
    # rollback db if using transactions
    return jsonify({"success": False, "message": "Server error!"}), 500


@app.route('/db/reset', methods=['POST'])
@basic_auth.login_required
def fl_restart():
    reset_db_values()
    return jsonify({"success": True})


@app.route('/db/get_values', methods=['GET'])
@basic_auth.login_required
def fl_get_values():
    ret_val = print_db_values()
    return jsonify(ret_val)


@app.route('/db/increase/<int:id>', methods=['POST'])
@basic_auth.login_required
def fl_inc_vals(id):
    increase_db_values(id)
    return jsonify({"success": True})


@app.route('/db/increase_locking/<int:id>', methods=['POST'])
@basic_auth.login_required
def fl_inc_vals_lock(id):
    increase_db_values_locking(id)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(ssl_context='adhoc')
