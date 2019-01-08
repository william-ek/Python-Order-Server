from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import exc


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/bobs_burgers_orders'
app.debug = False

db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String())
    total = db.Column(db.Integer())
    items = db.Column(JSON)

    def __init__(self, status, total, items):
        self.status = status
        self.total = total
        self.items = items

    def __repr__(self):
        return '<id {}>'.format(self.id)

    @staticmethod
    def to_dict(order):
        dct = {
            "id": order.id,
            "status": order.status,
            "total": order.total,
            "items": order.items,
        }

        return dct


    @staticmethod
    def to_list_dict(orders):
        return {
            "metaData": {
            },
            "items": [Order.to_dict(order) for order in orders]
        }

@app.route('/order/<id>', methods=['GET'])
def getOrder():
    try:
        results = db.session.query(Order).get(id)
        if results is None:
            return "record id {} is not found".format(id), 404
        response = Order.to_list_dict([results])
        return jsonify(response), 200
    except Exception as e:
        return "{}".format(e), 500

@app.route('/order', methods=['GET'])
def getOrders():
    results = Order.query.all()
    response = Order.to_list_dict(results)
    return jsonify(response), 200

@app.route('/order', methods=['POST'])
def createOrder():
    content = request.json
    print("Request: {}".format(content))
    order = Order(content['status'], content['total'], content['items'])
    try:
        db.session.add(order)
        db.session.commit()
        db.session.refresh(order)
        return jsonify(Order.to_list_dict([order])), 201
    except exc.IntegrityError as i:
        print(f"Integrity: {i.orig}")
        return "{}".format(i.orig), 409
    except Exception as e:
        print("Eception: {}".format(e))
        return "{}".format(e.orig), 500

if __name__ == '__main__':
    app.run(port=5001)