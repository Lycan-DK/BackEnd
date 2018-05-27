from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api
import uuid
import jwt
import datetime
from functools import wraps
import json
from flask_cors import CORS

app = Flask(__name__)
api= Api(app)
CORS(app)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data/User.db'

db= SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    token = db.Column(db.String(200))



class client(Resource):
    def get(self):
        users= User.query.all()
        output=[]
        for user in users:
            user_data={}
            user_data['public_id']= user.public_id
            user_data['name']= user.name
            user_data['password']= user.password
            user_data['admin']= user.admin
            user_data['Token']= user.token
            output.append(user_data)
            
        return {"users": output}
    
    def post(self):
        data= request.get_json()
        new_user= User(public_id=str(uuid.uuid4()), name=data['name'],password=data['password'],admin=False)
        db.session.add(new_user)
        db.session.commit()
        return {"Message ":"New user created"},200

class sinuser(Resource):
    def get(self,public_id):
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return {"message" : "no user found"}
        user_data={}
        user_data['public_id']= user.public_id
        user_data['name']= user.name
        user_data['password']= user.password
        user_data['admin']= user.admin
        return {'user':user_data}   
    
    def put(self,public_id):
        data= request.get_json()
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return {"message" : "no user found"}
        if (user.admin==False):
            user.admin=True
        else:
            user.admin=False
        db.session.commit()
        return {"message" : user.name+" is promoted to admin"}
    
    def delete(self,public_id):
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return {"message" : "no user found"}
        db.session.delete(user)
        db.session.commit()
        return {"message" : "user deleted"}

    

class login(Resource):
    def get(self):
        auth = request.authorization

        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required1!"'})

        user = User.query.filter_by(name=auth.username).first()

        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required2!"'})

        if (user.password== auth.password):
            token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            user.token= token.decode('UTF-8')
            db.session.commit()
            return jsonify({'token' : token.decode('UTF-8'), 'name': user.name,'admin':user.admin})
        
        

        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required3!"'})



api.add_resource(client ,'/user')
api.add_resource(sinuser,'/user/<public_id>')
api.add_resource(login ,'/login')



if __name__ == '__main__':
    app.run(debug = True)
