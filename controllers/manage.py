import sys
import os
sys.path.insert(1, '../models')
from tokens import Tokens
from departments import Departments
from streams import Streams
from admins import Admins
from counters import Counters
from sms import SMS
from main import app, db
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, SMS=SMS, Tokens=Tokens, Departments=Departments, Streams=Streams, Admins=Admins, Counters=Counters)