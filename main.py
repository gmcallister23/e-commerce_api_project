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
    Column('product_id', ForeignKey('products.id'), primary_key=True),
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
    orders = Mapped[List['Order']] = relationship('Order', back_populates='user')

#Product table
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[float] = mapped_column(Float(5), nullable=False)
    #Many-many - orders and products
    orders: Mapped[List['Order']] = relationship('Order', secodary=order_product, back_populates='products')

#Order table
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    #One to many - user --> orders
    user = Mapped['User'] = relationship('User', back_populates='orders')
    products = Mapped[List['Product']] = relationship('Product', secondary=order_product, back_populates='orders')

#Schemas
#User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    
#Order Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order

#Initialize Schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
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
@app.route('/users', methods=['PUT'])
def create_user():
    try:
        user_data = user_schema.load(request.json) #--> 'load' deserializes the json data into python formats
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], email=user_data['email'])
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


#Order Routes

with app.app_context():
    #db.drop_all()
    db.create_all()