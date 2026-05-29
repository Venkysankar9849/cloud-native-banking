"""Transaction Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.main import db, app
from app.models.user import Account, Transaction
from datetime import datetime
import uuid
transactions_bp = Blueprint('transactions', __name__)
@transactions_bp.route('/<int:account_id>/deposit', methods=['POST'])
@jwt_required()
def deposit(account_id):
"""Deposit funds to account"""
try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
if not account:
return jsonify({'error': 'Account not found'}), 404
        data = request.get_json()
        amount = float(data.get('amount', 0))
if amount <= 0:
return jsonify({'error': 'Amount must be positive'}), 400
# Create transaction
        reference_id = f"DEP-{uuid.uuid4().hex[:12].upper()}"
        transaction = Transaction(
            account_id=account_id,
            transaction_type='DEPOSIT',
            amount=amount,
            currency=account.currency,
            status='COMPLETED',
            reference_id=reference_id,
            description=data.get('description', 'Deposit'),
            completed_at=datetime.utcnow()
)
# Update account balance
        account.balance += amount
        account.updated_at = datetime.utcnow()
        db.session.add(transaction)
        db.session.commit()
         app.logger.info(f"Deposit: {amount} to account {account_id}, reference: {ref
return jsonify({
'message': 'Deposit successful',
'transaction': transaction.to_dict(),
'new_balance': float(account.balance)
}), 201
except Exception as e:
        db.session.rollback()
        app.logger.error(f"Deposit error: {str(e)}")
return jsonify({'error': str(e)}), 500
@transactions_bp.route('/<int:account_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw(account_id):
"""Withdraw funds from account"""
try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
if not account:
return jsonify({'error': 'Account not found'}), 404
        data = request.get_json()
        amount = float(data.get('amount', 0))
        if amount <= 0:
return jsonify({'error': 'Amount must be positive'}), 400
if account.balance < amount:
return jsonify({'error': 'Insufficient funds'}), 400
# Create transaction
        reference_id = f"WTH-{uuid.uuid4().hex[:12].upper()}"
        transaction = Transaction(
            account_id=account_id,
            transaction_type='WITHDRAWAL',
            amount=amount,
            currency=account.currency,
            status='COMPLETED',
            reference_id=reference_id,
            description=data.get('description', 'Withdrawal'),
            completed_at=datetime.utcnow()
)
# Update account balance
        account.balance -= amount
        account.updated_at = datetime.utcnow()
        db.session.add(transaction)
        db.session.commit()
        app.logger.info(f"Withdrawal: {amount} from account {account_id}, reference:
return jsonify({
'message': 'Withdrawal successful',
'transaction': transaction.to_dict(),
'new_balance': float(account.balance)
}), 201
except Exception as e:
        db.session.rollback()
        app.logger.error(f"Withdrawal error: {str(e)}")
return jsonify({'error': str(e)}), 500
@transactions_bp.route('/<int:account_id>/history', methods=['GET'])
@jwt_required()
def get_transaction_history(account_id):
"""Get transaction history"""
try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
if not account:
return jsonify({'error': 'Account not found'}), 404
# Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transactions = Transaction.query.filter_by(account_id=account_id)\
.order_by(Transaction.created_at.desc())\
.paginate(page=page, per_page=per_page)
return jsonify({
'transactions': [t.to_dict() for t in transactions.items],
'page': page,
'per_page': per_page,
'total': transactions.total,
'pages': transactions.pages
}), 200
except Exception as e:
        app.logger.error(f"Error fetching transaction history: {str(e)}")
return jsonify({'error': str(e)}), 500
