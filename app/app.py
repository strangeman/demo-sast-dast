from flask import session, Flask, jsonify, request, Response, render_template, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import json
import os
from faker import Faker
import base64

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['STATIC_FOLDER'] = "/"

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    ccn = db.Column(db.String(80), nullable = True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(150))

    def __repr__(self):
        return "<User {0} {1}>".format(self.first_name, self.last_name)

def has_no_empty_params(rule):
    default = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(default) >= len(arguments)


@app.before_first_request
def setup_users():

    db.create_all()

    # create fake customers with test data
    if not Customer.query.first():
        for i in range(0,5):
            fake = Faker()
            cust = Customer()
            cust.first_name = fake.first_name()
            cust.last_name = fake.last_name()
            cust.email = fake.simple_profile(sex = None)['mail']
            cust.username = fake.simple_profile(sex = None)['username']
            cust.password = str(base64.b64encode(os.urandom(16)))
            cust.ccn = fake.credit_card_number(card_type=None)
            db.session.add(cust)
            db.session.commit()

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')

@app.route('/get_all', methods = ['GET'])
def get_all():
    records = Customer.query.all()
    all_records = []
    for customer_record in records:
        all_records.append({'id': customer_record.id, 'firstname': customer_record.first_name,
                            'lastname': customer_record.last_name, 'email': customer_record.email,
                            'cc_num': customer_record.ccn, 'username': customer_record.username
                        })
    return jsonify(all_records),200

@app.route('/get/<customer_id>', methods = ['GET'])
def get_customer(customer_id):
    if customer_id:
        customer_record = Customer.query.from_statement(text("""SELECT * FROM Customer where id=%s""" % customer_id)).first()
        print(customer_record)
        if customer_record:
            customer_dict = {'id': customer_record.id, 'firstname': customer_record.first_name,
                            'lastname': customer_record.last_name, 'email': customer_record.email,
                            'cc_num': customer_record.ccn, 'username': customer_record.username
                        }
            return jsonify(customer_dict),200
        else:
            return jsonify({'Error': 'No Customer Found'}),404
    else:
        return jsonify({'Error': 'Invalid Request'}),400

@app.route('/add', methods = ['POST'])
def add_customer():
    try:
        content = request.json
        if content:
            username = content['username']
            password = content['password']
            first_name = content['first_name']
            last_name = content['last_name']
            email = content['email']
            ccn = content['ccn']
            cust = Customer(first_name, last_name, email, username, password, ccn)
            db.session.add(cust)
            db.session.commit()
            user_created = 'Customer: {0} has been created'.format(username)
            return jsonify({'Created': user_created}),200
    except Exception as e:
        return jsonify({'Error': str(e.message)}),404