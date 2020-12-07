import sys
import os
import logging
sys.path.insert(1, '../models')
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import and_
from config import DevConfig
from tokens import Tokens
from departments import Departments
from streams import Streams
from admins import Admins
from counters import Counters
from sms import SMS
from sound_setting import Sound
from datetime import datetime, timedelta
from api_handler import send_messages
from threading import Thread
template_dir = os.path.abspath('../templates')
static_dir = os.path.abspath('../static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(DevConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/version_1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db = SQLAlchemy(app)

#Admin related function 
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    admins = Admins.query.all()
    error = "Username or Password incorrect"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_names = [admin.name for admin in admins]
        if username in admin_names:
            admin_by_name = Admins.query.filter_by(name = username).first()
            admin_pass = admin_by_name.password
            if password == admin_pass:
                session['current_admin'] = username
                return redirect('/admin')
            else:
                return render_template('admin_login.html', error=error)
        else:
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')
@app.route('/admin/logout')
def admin_logout():
    if 'current_admin' in session:
        session.pop('current_admin',None)
    return redirect('/admin_login')
@app.route('/admin')
def admin():
    if 'current_admin' in session:
        return render_template('admin.html')
    else:
        return redirect('/admin_login')
@app.route('/dashboard')
def dashboard():
    return 'Dashboard'


#Token related functions
def _get_current_token():
    today = datetime.today().date()
    tokens = Tokens.query.filter(Tokens.date > today).all()
    if tokens:
        last_token = tokens[-1].token_day_number
        last_token = int(last_token)
        current_token = last_token + 1
        current_token = str(current_token).zfill(3)
        return current_token
    else:
        return "001"
    logging.critical(last_token)
def _get_attending(dept_id, stream_id):
    today = datetime.today().date()
    tokens = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                            Tokens.stream == stream_id)).all()
    remaining = len(tokens)
    return remaining
def _get_remaining_time(dept_id, stream_id):
    today = datetime.today().date()
    tokens = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                            Tokens.stream == stream_id)).all()
    stream_estimated_time = Streams.query.filter_by(id=stream_id).first()
    estimated_time = stream_estimated_time.estimated_time
    return estimated_time
@app.route('/', methods=['GET', 'POST'])
@app.route('/token_interface', methods=['GET', 'POST'])
def token_interface():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        dept_id = request.form['departments']
        stream_id = request.form['streams']
        token_day_number = _get_current_token()
        position = _get_attending(dept_id, stream_id)
        remaining_time = _get_remaining_time(dept_id, stream_id)
        token = Tokens(token_day_number=token_day_number, phone_number=phone_number,
                        department=dept_id, stream=stream_id)
        db.session.add(token)
        db.session.commit()
        token_id = token.id
        dept_name = Departments.query.filter_by(id=dept_id).first().name
        stream_name = Streams.query.filter_by(id=stream_id).first().name
        return render_template('generated_token.html', dept_name=dept_name, 
            token_number=token_day_number, position=position, remaining_time=remaining_time, token_id=token_id, stream_name=stream_name)
    departments = Departments.query.all()
    streams = Streams.query.all()
    return render_template('token_interface.html', departments= departments, streams=streams)
@app.route('/token/cancel/<int:token_id>')
def cancel_token(token_id):
    token = Tokens.query.filter_by(id=token_id).first()
    token.state = 'cancel'
    db.session.merge(token)
    db.session.commit()
    return redirect('/token_interface')
@app.route('/token_list')
def tokens_list():
    today = datetime.today().date()
    tokens = Tokens.query.order_by(Tokens.token_day_number.desc()).filter(and_(Tokens.date > today)).all()
    departments = Departments
    streams = Streams
    counters = Counters
    return render_template('token.html', tokens=tokens, streams= streams, departments=departments, counters=counters)

#Departments related functions
@app.route('/departments/new',  methods=['GET', 'POST'])
def create_new_department():
    if request.method == 'POST':
        name = request.form['name']
        dept = Departments(name=name)
        db.session.add(dept)
        db.session.commit()
        return redirect('/departments_list')
    return render_template('new_department.html')
@app.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
def edit_department(dept_id):
    department = Departments.query.filter_by(id=dept_id).first()
    if request.method == 'POST':
        name = request.form['name']
        dept_name = Departments.query.filter_by(id=dept_id).first()
        dept_name.name = name
        db.session.merge(dept_name)
        db.session.commit()
        return redirect('/departments_list')
    return render_template('dept_edit.html', department=department)
@app.route('/departments/delete/<int:dept_id>')
def delete_department(dept_id):
    department = Departments.query.filter_by(id=dept_id).first()
    current_db_session = db.session.object_session(department)
    current_db_session.delete(department)
    current_db_session.commit()
    departments = Departments.query.all()
    return redirect('/departments_list')
@app.route('/departments_list')
def departments_list():
    departments = Departments.query.all()
    return render_template('departments.html',departments=departments)

#Streams related functions

@app.route('/streams_list')
def streams_list():
    streams = Streams.query.all()
    departments = Departments
    return render_template('streams.html',streams=streams, departments=departments)
@app.route('/streams/new',  methods=['GET', 'POST'])
def create_new_stream():
    if request.method == 'POST':
        name = request.form['name']
        dept_id = request.form['departments']
        estimated_time = request.form['estimated_time']
        stream = Streams(name=name, dept_id=dept_id, estimated_time=estimated_time)
        db.session.add(stream)
        db.session.commit()
        return redirect('/streams_list')
    departments = Departments.query.all()
    return render_template('new_stream.html', departments=departments)
@app.route('/streams/edit/<int:stream_id>', methods=['GET', 'POST'])
def edit_stream(stream_id):
    stream = Streams.query.filter_by(id=stream_id).first()
    if request.method == 'POST':
        name = request.form['name']
        dept_id = request.form['departments']
        estimated_time = request.form['estimated_time']
        stream = Streams.query.filter_by(id=stream_id).first()
        if name != "":
            stream.name = name
        stream.dept_id = dept_id
        stream.estimated_time = int(estimated_time)
        db.session.merge(stream)
        db.session.commit()
        return redirect('/streams_list')
    departments = Departments.query.all()
    return render_template('stream_edit.html', stream=stream, departments=departments)
@app.route('/streams/delete/<int:stream_id>')
def delete_stream(stream_id):
    stream = Streams.query.filter_by(id=stream_id).first()
    current_db_session = db.session.object_session(stream)
    current_db_session.delete(stream)
    current_db_session.commit()
    return redirect('/streams_list')

#Counters related functions

@app.route('/counters_list')
def counters_list():
    counters = Counters.query.all()
    return render_template('counters.html',counters=counters)
@app.route('/counters/new',  methods=['GET', 'POST'])
def create_new_counter():
    if request.method == 'POST':
        name = request.form['name']
        counter = Counters(name=name)
        db.session.add(counter)
        db.session.commit()
        return redirect('/counters_list')
    return render_template('new_counter.html')
@app.route('/counters/edit/<int:counter_id>', methods=['GET', 'POST'])
def edit_counter(counter_id):
    counter = Counters.query.filter_by(id=counter_id).first()
    if request.method == 'POST':
        name = request.form['name']
        counter = Counters.query.filter_by(id=counter_id).first()
        counter.name = name
        db.session.merge(counter)
        db.session.commit()
        return redirect('/counters_list')
    return render_template('counter_edit.html', counter=counter)
@app.route('/counters/delete/<int:counter_id>')
def delete_counter(counter_id):
    counter = Counters.query.filter_by(id=counter_id).first()
    current_db_session = db.session.object_session(counter)
    current_db_session.delete(counter)
    current_db_session.commit()
    return redirect('/counters_list')

@app.route('/counter/login', methods=['GET', 'POST'])
def counter_login():
    if request.method == 'POST':
        name = request.form['name']
        try:
            counter_id = Counters.query.filter(Counters.name == name).first().id  
            return redirect('/queue/processing/dashboard/{0}'.format(counter_id))
        except Exception as exp:
            error = "Counter does not exist"
            logging.critical(exp)
            return render_template('login_counter.html', error=error)
    counters = Counters.query.all()
    return render_template('login_counter.html', counters=counters)
@app.route('/counter/logout', methods=['GET', 'POST'])
def counter_logout():
    try:
        session.pop('dept_id', None)
        session.pop('stream_id', None)
        session.pop('counter_id', None)
    except Exception as exp:
        logging.critical(exp)
    return redirect('/counter/login')
#Queue processing related functions
@app.route('/queue/processing/dashboard/<int:counter_id>', methods=['GET', 'POST'])
@app.route('/queue/processing/dashboard/<int:counter_id>/<int:close>', methods=['GET', 'POST'])
def queue_processing_dashboard(counter_id, close=0):
    departments = Departments.query.all()
    streams = Streams.query.all()
    if request.method == 'POST':
        dept_id = request.form['departments']
        stream_id = request.form['streams']
        counter_id = counter_id
        session['dept_id'] = dept_id
        session['counter_id'] = counter_id
        session['stream_id'] = stream_id
        today = datetime.today().date()
        tokens = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                        Tokens.stream == stream_id)).all()
        departments = Departments
        streams = Streams
        counters = Counters
        return render_template('queue_processing.html', dept_id=dept_id, stream_id=stream_id, counter_id=counter_id, 
                              tokens=tokens, counters=counters, departments=departments, streams=streams)
    if not close:
        if 'dept_id' in session:
            today = datetime.today().date()
            dept_id = session['dept_id']
            stream_id = session['stream_id']
            counter_id = session['counter_id']
            tokens = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                            Tokens.stream == stream_id)).all()
            departments = Departments
            streams = Streams
            counters = Counters
            return render_template('queue_processing.html', dept_id=dept_id, stream_id=stream_id, counter_id=counter_id, 
                                tokens=tokens, counters=counters, departments=departments, streams=streams)
    return render_template('queue_dashboard.html', streams=streams, departments=departments)

@app.route('/queue/token/processing/', methods=['GET', 'POST'])
@app.route('/queue/token/processing/<int:done>', methods=['GET', 'POST'])
def token_processing(done=0):
    today = datetime.today().date()
    if done:
        if 'token_id' in session:
            token_id = session['token_id']
            token = Tokens.query.filter_by(id = token_id ).first()
            counter_id = session['counter_id']
            token.processed_by = counter_id
            token.state = 'done'
            db.session.merge(token)
            db.session.commit()
            session.pop('token_id', None)
            return redirect('/queue/processing/dashboard/{0}'.format(session['counter_id']))
    else:
        dept_id = session['dept_id']
        stream_id = session['stream_id']
        counter_id = session['counter_id']
        dept_name = Departments.query.filter_by(id=dept_id).first().name
        stream_name = Streams.query.filter_by(id=stream_id).first().name
        counter_name = Counters.query.filter_by(id=counter_id).first().name
        token = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                        Tokens.stream == stream_id)).first()
        tokens = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                        Tokens.stream == stream_id)).all()
        sms = SMS.query.first()
        try:
            t = Thread(target=send_messages(tokens, sms))
            t.start()
        except Exception as exp:
            logging.critical(exp)
        
        token_number = token.token_day_number
        token_id = token.id
        token.state = 'inprogress'
        state = token.state
        db.session.merge(token)
        db.session.commit()
        session['token_id'] = token_id
        return render_template('queue_token_processing.html', token_number=token_number, department=dept_name,
                                counter=counter_name, stream=stream_name, state=state)

#SMS related
@app.route('/sms/setting', methods=['GET', 'POST'])
def sms_setting():
    sms = SMS.query.all()
    if request.method == 'POST':
        text = request.form['text']
        text_to_next = request.form['text_to_next']
        if sms:
            #update
            sms = sms[0]
            sms.text = text
            sms.text_to_next = text_to_next
            db.session.merge(sms)
            db.session.commit()
            return redirect('/sms_list')
        else:
            #create
            sms = SMS(text=text, text_to_next=text_to_next)
            db.session.add(sms)
            db.session.commit()
            return redirect('/sms_list')
    return render_template('sms_setting.html')
@app.route('/sms_list')
def sms():
    sms = SMS.query.first()
    return render_template('sms.html', sms=sms)

#Sound player related

@app.route('/sound/setting', methods=['GET', 'POST'])
def sound_setting():
    sound = Sound.query.all()
    if request.method == 'POST':
        repetition = request.form['repetition']
        if sound:
            #update
            sound = sound[0]
            sound.repetition = repetition
            db.session.merge(sound)
            db.session.commit()
            return redirect('/sound_setting_list')
        else:
            #create
            sound = Sound(repetition=repetition)
            db.session.add(sound)
            db.session.commit()
            return redirect('/sound_setting_list')
    return render_template('sound_player_setting.html')
@app.route('/sound_setting_list')
def sound():
    audio = Sound.query.first()
    return render_template('sound_player.html', audio=audio)
if __name__ == '__main__':
    app.run()
