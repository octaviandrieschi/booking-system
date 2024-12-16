# Utilitar pentru autentificare și autorizare
# Oferă decoratori și funcții pentru gestionarea autentificării și rolurilor

import jwt
from functools import wraps
from flask import request, jsonify
from config import Config

def token_required(f):
    """
    Decorator pentru protejarea rutelor care necesită autentificare
    Verifică prezența și validitatea token-ului JWT
    
    Returns:
        function: Funcția decorată care primește user_id ca parametru
        sau răspuns de eroare dacă autentificarea eșuează
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        # Extrage token-ul din header
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'message': 'Token lipsă'}), 401
            
        try:
            # Verifică și decodează token-ul
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
            return f(current_user_id, *args, **kwargs)
        except:
            return jsonify({'message': 'Token invalid'}), 401
            
    return decorated

def admin_required(f):
    """
    Decorator pentru protejarea rutelor administrative
    Verifică dacă utilizatorul are rol de admin
    
    Returns:
        function: Funcția decorată care primește user_id ca parametru
        sau răspuns de eroare dacă utilizatorul nu este admin
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'message': 'Token lipsă'}), 401
            
        try:
            # Verifică rolul utilizatorului
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            if data['role'] != 'admin':
                return jsonify({'message': 'Acces interzis'}), 403
            return f(data['user_id'], *args, **kwargs)
        except:
            return jsonify({'message': 'Token invalid'}), 401
            
    return decorated

def get_token_data():
    """
    Extrage datele din token-ul JWT curent
    
    Returns:
        dict: Datele decodate din token sau None dacă token-ul lipsește/este invalid
    """
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except:
            return None
    return None 