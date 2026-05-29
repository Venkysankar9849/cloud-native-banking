"""User Model"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.main import db
class User(db.Model):
    __tablename__ = 'users'
id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.u
    last_login = db.Column(db.DateTime, nullable=True)
# Relationships
    accounts = db.relationship('Account', backref='user', lazy='dynamic', cascade='a
def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256'
def check_password(self, password):
return check_password_hash(self.password_hash, password)
def to_dict(self):
return {
'id': self.id,
'email': self.email,
'username': self.username,
'first_name': self.first_name,
'last_name': self.last_name,
'is_active': self.is_active,
'is_verified': self.is_verified,
'created_at': self.created_at.isoformat(),
}
def __repr__(self):
return f'<User {self.username}>'
class Account(db.Model):
 __tablename__ = 'accounts'
id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=Tru
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index
    account_type = db.Column(db.String(50), nullable=False) # SAVINGS, CHECKING, BU
    balance = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.u
# Relationships
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic',
def to_dict(self):
return {
'id': self.id,
'account_number': self.account_number,
'account_type': self.account_type,
'balance': float(self.balance),
'currency': self.currency,
'is_active': self.is_active,
'created_at': self.created_at.isoformat(),
}
def __repr__(self):
return f'<Account {self.account_number}>'
class Transaction(db.Model):
    __tablename__ = 'transactions'
id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False,
    transaction_type = db.Column(db.String(50), nullable=False) # DEPOSIT, WITHDRAW
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)
    status = db.Column(db.String(50), default='PENDING', nullable=False) # PENDING,
    description = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
def to_dict(self):
return {
'id': self.id,
'transaction_type': self.transaction_type,
'amount': float(self.amount),
'currency': self.currency,
'status': self.status,
'reference_id': self.reference_id,
'created_at': self.created_at.isoformat(),
}
def __repr__(self):
return f'<Transaction {self.reference_id}>'