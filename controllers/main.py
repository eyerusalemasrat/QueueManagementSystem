from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import sys
import os
sys.path.insert(1, '../models')
template_dir = os.path.abspath('../templates')
from tokens import Token
app = Flask(__name__, template_folder=template_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/queue_mangement_system'
db = SQLAlchemy(app)
@app.route('/token_interface', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        Token.create(phone_number=phone_number)
    return render_template('token_interface.html')
@app.cli.command('initdb')
def create_db():
    '''Create database'''
    db.drop_all()
    db.create_all()
@app.cli.command('bootstrap')
def bootstrap_data():
    db.drop_all()
    db.create_all()
    db.session.add(
        Token(
            phone_number='0922874972'
        )
    )
    db.session.commit()
if __name__ == '__main__':
    app.run(debug=True)