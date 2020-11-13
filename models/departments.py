import datetime
import model_config
db = model_config.db
class Departments(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    streams = db.relationship('Streams', backref='departments', lazy=True)
    
