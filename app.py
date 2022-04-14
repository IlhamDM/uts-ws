#18090026_Muhammad Affry_6D
#18090122_Dimas Ilham M_6D
#18090139_Alfan Nur Rabbani_6D
#19090031_Rizqi Amalia_6D

from datetime import datetime
import os,random, string
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask import Flask, jsonify, request
app = Flask(__name__)

app = Flask(__name__)

app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(app_dir, "touring.db"))
db = SQLAlchemy(app)

ma = Marshmallow(app)

class LogSchemas(ma.Schema):
    class Meta:
        fields = ('username', 'log_lat','log_lng','created_at')


logsSchemas = LogSchemas(many=True)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    token = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username,password):
        self.username = username
        self.password= password


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_creator = db.Column(db.String(20), unique=False, nullable=False)
    event_name = db.Column(db.String(20), unique=False, nullable=False)
    event_start_time = db.Column(db.DateTime)
    event_end_time = db.Column(db.DateTime)
    event_start_lat = db.Column(db.String(20), unique=False, nullable=False)
    event_finish_lat = db.Column(db.String(20), unique=False, nullable=False)
    event_start_lng = db.Column(db.String(20), unique=False, nullable=False)
    event_finish_lng = db.Column(db.String(20), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, event_creator, event_name, event_start_time, event_end_time, event_start_lat, event_finish_lat, event_start_lng, event_finish_lng):
        self.event_creator = event_creator
        self.event_name = event_name
        self.event_start_time = event_start_time
        self.event_end_time = event_end_time
        self.event_start_lat = event_start_lat
        self.event_finish_lat = event_finish_lat
        self.event_start_lng = event_start_lng
        self.event_finish_lng = event_finish_lng

class Logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    event_name = db.Column(db.String(20), unique=False, nullable=False)
    log_lat = db.Column(db.String(20), unique=False, nullable=False)
    log_lng = db.Column(db.String(20), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, event_name, log_lat, log_lng):
        self.username = username
        self.event_name = event_name
        self.log_lat = log_lat
        self.log_lng = log_lng


if not os.path.exists(os.path.join(app_dir, 'touring.db')):
    db.create_all()

@app.route("/api/v1/users/create", methods=["POST"])
def add_user():
    username = request.json['username']
    password = request.json['password']


    print(username, password)
    new_user = Users(username, password)

    db.session.add(new_user)
    db.session.commit()

    msg = {'message': 'registrasi sukses'}
    return jsonify(msg)

@app.route("/api/v1/users/login", methods=["POST"])
def login():
    username = request.json['username']
    password = request.json['password']

    account = Users.query.filter_by(username=username, password=password).first()

    if account:
        token = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=10))

        Users.query.filter_by(username=username, password=password).update({'token': token})
        db.session.commit()

        data = {'msg': 'login sukses', 'token': token}
        return jsonify(data)
    else:
        data = {'result': 'login gagal'}
        return jsonify(data)

@app.route("/api/v1/events/create", methods=["POST"])
def add_event():
    token = request.json['token']
    user = Users.query.filter_by(token=token).first()
    if(user):
        event_start = request.json['event_start_time']
        event_end = request.json['event_end_time']
        event_creator = user.username
        event_name = request.json['event_name']
        event_start_time = datetime.strptime(event_start, "%Y-%m-%d %H:%M:%S")
        event_end_time = datetime.strptime(event_end, "%Y-%m-%d %H:%M:%S")
        event_start_lat = request.json['event_start_lat']
        event_start_lng = request.json['event_start_lng']
        event_finish_lat = request.json['event_start_lat']
        event_finish_lng = request.json['event_start_lng']


        new_event = Events(event_creator,event_name, event_start_time, event_end_time, event_start_lat, event_start_lng, event_finish_lat, event_finish_lng)

        db.session.add(new_event)
        db.session.commit()

        msg = {'message': 'membuat event sukses'}
        return jsonify(msg)

    else:
        res={"message":"Unauthorized"}
        return jsonify(res)

@app.route("/api/v1/events/log", methods=["POST"])
def add_log():
    token = request.json['token']
    user = Users.query.filter_by(token=token).first()
    if (user):
        username = user.username
        event_name = request.json['event_name']
        log_lat = request.json['log_lat']
        log_lng = request.json['log_lng']

        new_log = Logs(username, event_name, log_lat, log_lng)

        db.session.add(new_log)
        db.session.commit()

        msg = {'message': 'sukses mencatat posisi terbaru'}
        return jsonify(msg)
    else:
        res = {"message": "Unauthorized"}
        return jsonify(res)
@app.route("/api/v1/events/logs", methods=['GET'])
def see_log():
    token = request.json['token']
    user = Users.query.filter_by(token=token).first()
    if(user):
        event_name = request.json['event_name']

        allLogs=Logs.query.filter(Logs.event_name == event_name).order_by(Logs.created_at.desc())
        result = logsSchemas.dump(allLogs)
        return jsonify(result)
    else:
        res = {"message": "Unauthorized"}
        return jsonify(res)



if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=7000)
