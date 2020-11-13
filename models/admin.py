import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.insert(1, '../controllers')
from mixin import ModelMixin
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/queue_mangement_system'
db = SQLAlchemy(app) 
class Admin(ModelMixin, db.Model):
    __tablename__ = 'admin.admin'
    id = db.Column(db.Integer, primary_key=True)
    #token_day_number = db.Column(db.String(10), )
    name = db.Column(db.String(20), nullable=False)
  

    