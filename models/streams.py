import datetime
import model_config
db = model_config.db
from departments import Departments
dept = Departments
class Streams(db.Model):
    __tablename__ = "streams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey(dept.id), nullable=False)

