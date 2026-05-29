"""Account Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.main import db, app
from app.models.user import User, Account
import uuid
accounts_bp = Blueprint('accounts', __name__)
@accounts_bp.route('', methods=['POST'])
@jwt_required()
def create_account():
"""Create new account"""
try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
if not user:
return jsonify({'error': 'User not found'}), 404
        data = request.get_json()
if 'account_type' not in data:
return jsonify({'error': 'Account type required'}), 400
# Generate account number
        account_number = f"ACC-{user_id}-{uuid.uuid4().hex[:8].upper()}"
        account = Account(
            account_number=account_number,
            user_id=user_id,
            account_type=data['account_type'],
            balance=data.get('initial_balance', 0),
            currency=data.get('currency', 'USD')
)
        db.session.add(account)
        db.session.commit()
        app.logger.info(f"Account created: {account_number} for user {user_id}")
return jsonify({
'message': 'Account created successfully',
'account': account.to_dict()
}), 201
except Exception as e:
        db.session.rollback()
        app.logger.error(f"Account creation error: {str(e)}")
return jsonify({'error': str(e)}), 500
@accounts_bp.route('', methods=['GET'])
@jwt_required()
def get_accounts():
"""Get all accounts for user"""
try:
        user_id = get_jwt_identity()
        accounts = Account.query.filter_by(user_id=user_id).all()
return jsonify({
'accounts': [acc.to_dict() for acc in accounts],
'count': len(accounts)
}), 200
except Exception as e:
        app.logger.error(f"Error fetching accounts: {str(e)}")
return jsonify({'error': str(e)}), 500
@accounts_bp.route('/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
"""Get account details"""
try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
if not account:
return jsonify({'error': 'Account not found'}), 404
return jsonify({'account': account.to_dict()}), 200
except Exception as e:
        app.logger.error(f"Error fetching account: {str(e)}")
return jsonify({'error': str(e)}), 500