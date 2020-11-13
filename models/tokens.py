import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.insert(1, '../controllers')
from mixin import ModelMixin
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/queue_mangement_system'
db = SQLAlchemy(app) 
class Token(ModelMixin, db.Model):
    __tablename__ = 'token.token'
    id = db.Column(db.Integer, primary_key=True)
    #token_day_number = db.Column(db.String(10), )
    phone_number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    '''department = db.relationship(
        'Departments', backref="name", lazy="select", 
    )
    streams = db.relationship(
        'Streams', backref="name", lazy="select", 
    )'''
    def __repr__(self):
        return '<Token %r>' % self.phone_number
    
