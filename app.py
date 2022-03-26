        #NAMA KELOMPOK
    #Ilham Maulana Fajar Sidik (19090064)
    #Doni Cahya Adi Saputra (19090114)

from fileinput import filename
import json
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
import os
import datetime


app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

# Konfigurasi DB
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SECRET_KEY'] = 'XXXXXX'

class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    token = db.Column(db.String(200))
db.create_all()

# Membuat username admin
class signup(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')
        
        if dataUsername and dataPassword:
            tokenreg = jwt.encode({ "username":dataUsername, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            dataModel = AuthModel(username=dataUsername, password=dataPassword, token = tokenreg)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"success" : True, "Token":tokenreg}), 200)
        return jsonify({"success" : False,"msg":"Username dan Password harus diisi"})


class Login(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')
        
        queryUsername = [data.username for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]
        if dataUsername in queryUsername and dataPassword in queryPassword:
            token = jwt.encode({ "username":queryUsername, "exp":datetime.datetime.utcnow()+ datetime.timedelta(minutes=10)}, 
            app.config['SECRET_KEY'], algorithm="HS256")
            DB_user = AuthModel.query.filter_by(username=dataUsername).first()
            DB_user.token = token
            db.session.commit()
            return make_response(jsonify({"msg":"Login Sukses", "token":token}), 200)
        return jsonify({"msg":"Login Gagal, Silahkan Coba Lagi!"})

class info(Resource):
    def post(self):
        dataToken = request.form.get('token')
        queryToken = [data.token for data in AuthModel.query.all()]
        if dataToken in queryToken:
            DB_user = AuthModel.query.filter_by(token=dataToken).first()
            return make_response(jsonify({"username": DB_user.username}), 200)
        return jsonify({"success" : False})

#API
api.add_resource(Login, "/api/v1/login", methods=["POST"])
api.add_resource(signup, "/api/v2/signup", methods=["POST"])
api.add_resource(info, "/api/v2/users/info", methods=["POST"])
if __name__ == "__main__":
    app.run(port=4000,debug=True)

