import datetime
import model_config
db = model_config.db
from departments import Departments
from streams import Streams
from counters import Counters
dept = Departments
streams = Streams
counters = Counters
class Tokens(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token_day_number = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    state = db.Column(db.String(10), default='waiting')
    department = db.Column(db.Integer, db.ForeignKey(dept.id))
    stream = db.Column(db.Integer, db.ForeignKey(streams.id))
    processed_by = db.Column(db.Integer, db.ForeignKey(counters.id))
    def __repr__(self):
        return '<Token %r>' % self.phone_number
