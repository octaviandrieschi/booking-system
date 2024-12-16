from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from app.models.user import User
from config import Config

bp = Blueprint('auth', __name__, url_prefix='/api')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.get_by_email(data['email']):
        return jsonify({'message': 'Email-ul este deja înregistrat!'}), 400
    
    user_id = User.create(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    return jsonify({'message': 'Înregistrare reușită!'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.get_by_email(data['email'])
    if not user:
        return jsonify({'message': 'Email sau parolă incorectă!'}), 401
    
    
    if not User.verify_password(user['password'], data['password']):
        return jsonify({'message': 'Email sau parolă incorectă!'}), 401
    
    token = jwt.encode({
        'user_id': user['id'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(days=1)
    }, Config.SECRET_KEY)
    
    
    return jsonify({
        'token': token,
        'username': user['username'],
        'role': user['role']
    }) 