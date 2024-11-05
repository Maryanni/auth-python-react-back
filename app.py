from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt, generate_password_hash
from models import db, User
import re

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auht-4geek.db"
app.config["JWT_SECRET_KEY"] = "secret-key"
app.config["SECRET_KEY"] = "contraseña-auth"
JWTManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)
Migrate(app, db)
CORS(app)


@app.route("/", methods=["GET"])
def people():
    return "<h1>Startwars rest api</h1>"


@app.route("/user", methods=["GET", "POST"])
def user():
    user = User()

    if request.method == "POST":
            first_name = request.json.get("first_name")
            last_name = request.json.get("last_name")
            email = request.json.get("email")
            password = request.json.get("password")

            existing_user = User.query.filter_by(email=email).first()
           
            if existing_user:
               return jsonify({"msg": "Email already registered"}), 409

            if email is not None:
               email_re = r"^\S+@\S+\.\S+$"
               if re.match(email_re, email):
                  user.email = email
               else:
                   return jsonify({"msg": "Email with invalid format"}), 400
            else:
               return jsonify({"msg": "Email cannot be empty"}), 400
            
            if password is not None:
                password_re = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
                if re.match(password_re, password):
                    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                    user.password = password_hash
                else:
                    return({"msg":"Password with invalid format"}), 400
            else:
               return jsonify({"msg": "Password cannot be empty"}), 400
            
            user.first_name = first_name
            user.last_name = last_name

            db.session.add(user)
            db.session.commit()

            return jsonify({
                    "user_id": user.id,
                    "user_first_name": user.first_name,
                    "user_last_name": user.last_name
            }), 201

    if request.method == "GET":
        users = User.query.all()
        users = list(map(lambda user: user.serialize(), users))

        return jsonify(users)
    

@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    password = request.json.get("password")

    if password is None:
        return jsonify({"msg": "Password is required"}), 400
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404 
  
    if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=email)
            return jsonify({"msg": "Success", "access_token": access_token}), 200
    else:
        return jsonify({"msg": "Invalid password"}), 404


if __name__ == "__main__":
    app.run(host="localhost", port=5051, debug=True)