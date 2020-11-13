import datetime
import model_config
db = model_config.db
class Counters(db.Model):
    __tablename__ = "counters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

