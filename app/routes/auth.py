"""Authentication Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from app.main import db, app
from app.models.user import User
from datetime import datetime
import uuid
auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['POST'])
def register():
"""User Registration"""
try:
        data = request.get_json()
# Validation
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name
if not all(field in data for field in required_fields):
return jsonify({'error': 'Missing required fields'}), 400
# Check if user exists
if User.query.filter_by(email=data['email']).first():
return jsonify({'error': 'Email already registered'}), 409
if User.query.filter_by(username=data['username']).first():
return jsonify({'error': 'Username already taken'}), 409
# Create user
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number')
)
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"New user registered: {user.email}")
return jsonify({
'message': 'User registered successfully',
'user': user.to_dict()
}), 201
except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {str(e)}")
return jsonify({'error': str(e)}), 500
@auth_bp.route('/login', methods=['POST'])
def login():
"""User Login"""
try:
        data = request.get_json()
if not data.get('email') or not data.get('password'):
return jsonify({'error': 'Email and password required'}), 400
        user = User.query.filter_by(email=data['email']).first()
if not user or not user.check_password(data['password']):
return jsonify({'error': 'Invalid credentials'}), 401
if not user.is_active:
return jsonify({'error': 'User account is inactive'}), 403
# Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
# Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        app.logger.info(f"User login successful: {user.email}")
return jsonify({
'message': 'Login successful',
'access_token': access_token,
'refresh_token': refresh_token,
'user': user.to_dict()
}), 200
except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
return jsonify({'error': str(e)}), 500
@auth_bp.route('/verify', methods=['GET'])
def verify_token():
"""Verify JWT Token"""
try:
from flask_jwt_extended import jwt_required, get_jwt_identity
@jwt_required()
def verify():
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
return jsonify({'valid': True, 'user': user.to_dict()}), 200
return verify()
except Exception as e:
return jsonify({'error': str(e)}), 401