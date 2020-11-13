import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from controllers.mixin import ModelMixin
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/queue_mangement_system'
db = SQLAlchemy(app) 

class Departments(db.Model):
    __tablename__ = "departments.departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=)