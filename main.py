from __future__ import annotations
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float, DateTime, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from marshmallow import ValidationError 
from typing import List, Optional
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Vjzs3455@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Base model

class Base(DeclarativeBase):
    pass

#Initialize SQLAlchemy and Marshmallow - creates the engine and connects to the database
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

#Order_Product association table
order_product = Table(
    'order_product', 
    Base.metadata,
    Column('product_id', ForeignKey('products.id'), primary_key=True, unique=True),
    Column('order_id', ForeignKey('orders.id'), primary_key=True)
)

#Models
#User Table
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    #One to many - user to orders
    orders: Mapped[List['Order']] = relationship('Order', back_populates='user') #Debugged with ChatGPT - orders = xxxx to orders:xxx, updated the rest that had '=' instead of ':'

#Product table
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[float] = mapped_column(Float(5), nullable=False)
    #Many-many - orders and products
    orders: Mapped[List['Order']] = relationship('Order', secondary=order_product, back_populates='products')

#Order table
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    #One to many - user --> orders
    user: Mapped['User'] = relationship('User', back_populates='orders')
    products: Mapped[List['Product']] = relationship('Product', secondary=order_product, back_populates='orders')

#Schemas
#User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User; include_fk=True

#Product Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
    
#Order Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order

#Initialize Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

#Routes

#User Routes
#read all users
@app.route('/users', methods = ['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

#read an individual user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200

#create a new user POST
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json) #--> 'load' deserializes the json data into python formats
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], address=user_data['address'], email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201 #---> this returns the new data in json format

#Update a user by id <int:id> 'PUT'
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({'messages': 'Invalid user id'}), 400
    
    try:
        user_data = user_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']

    db.session.commit()
    return user_schema.jsonify(user), 200

#Delete a user by id 'DELETE'
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({'message': f'Invalid user id.'})
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'Successfully delete user {id}'}), 200
 
#Product Routes

#Read all products 'GET'
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200

#Read product by id <int:id> 'GET'
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)

    return product_schema.jsonify(product)

#Add product 'POST'
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

#Update a product 'PUT'
@app.route('/products', methods=['PUT'])
def update_product():
    product = db.session.get(Product, id)

    if not product:
        return jsonify({'messages': 'Invalid product id'})
    
    try:
        product_data = product_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['name']
    product.price = product_data['price']
    
    db.session.commit()
    return product_schema.jsonify(product), 200

#Delete a product by id <int:id> 'DELETE'
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({'messages': 'Invalid product id'}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'messages': f'Successfully deleted product {id}'})

#Order Routes

#Create a new order - 'POST'
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data=order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order=Order(
        user_id=order_data['user_id'], 
        order_date=order_data['order_date'])
    db.session.add(new_order)
    db.session.commit()

#Add a product to an order - prevent duplicates 'PUT'
@app.route('/orders/<int:order_id>/add_product/<product_id>', methods=['PUT'])
def add_product(product_id, order_id):
    product = db.session.get(Product, product_id)
    order = db.session.get(Order, order_id)

    if product in order:
        return{'error': 'Cannot have more than one product in an order.'}

    product.orders.append(order)
    db.session.commit()

#Remove a product from an order - 'DELETE'
app.route('/orders/<int:order_id>/remove_product/<product_id>')
def remove_product(product_id, order_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    db.session.delete(product)
    db.session.commit
    return jsonify({'message': f'Successfully deleted {product_id} from {order_id}'})

#Get all orders for a user 'GET'
app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_order(user_id):

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 400
    
    #query = select(Order, user_id)
    #orders = db.session.execute().scalars().all()
    orders = Order.query.filter_by(user_id='user_id').all()
    return order_schema.dump(orders), 200

#Get all products in an order 'GET'
app.route('/orders/<order_id>/products', methods=['GET'])
def get_products(order_id):

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'message': f'Order not found'}), 400
    
    product = Product.query.filter_by(order_id='order_id').all()
    return product_schema.dump(product), 200

if __name__ == '__main__':

    with app.app_context():
        db.drop_all()
        db.create_all()

    app.run(debug=True)