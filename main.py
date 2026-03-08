from __future__ import annotations
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Table, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from marshmallow import ValidationError 
from typing import List, Optional

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

#Product table

#Order table



#Schemas
#User Schema

#Order Schema

#Routes

#User Routes

#Product Routes

#Order Routes

with app.app_context():
    #db.drop_all()
    db.create_all()