import sys
import os
import logging
sys.path.insert(1, '../models')
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig
from tokens import Tokens
from departments import Departments
from streams import Streams
from admins import Admins
from counters import Counters
template_dir = os.path.abspath('../templates')
static_dir = os.path.abspath('../static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(DevConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/version_1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
@app.route('/dashboard')
def dashboard():
    return 'Dashboard'
@app.route('/counters')
def counters():
    return 'counters'
@app.route('/token_interface', methods=['GET', 'POST'])
def token_interface():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        dept_id = request.form['departments']
        stream_id = request.form['streams']
        '''token = Tokens(phone_number=phone_number)
        db.session.add(token)
        db.session.commit()'''
    departments = Departments.query.all()
    streams = Streams.query.all()
    dept_name = [departments.name for departments in departments]
    stream_name = [streams.name for streams in streams]
    logging.critical(len(dept_name))
    for dept in dept_name:
        logging.critical(dept)
    return render_template('token_interface.html', departments= dept_name, streams=stream_name)
@app.route('/admin')
def admin():
    return render_template('admin.html')
@app.route('/token_list')
def token_list():
    tokens = Tokens.query.all()
    departments = Departments
    streams = Streams
    return render_template('token.html', tokens=tokens, streams= streams, departments=departments)
if __name__ == '__main__':
    app.run(DEBUG=True)