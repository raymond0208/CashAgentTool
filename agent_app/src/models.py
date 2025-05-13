from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_transaction_user'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

class InitialBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_initial_balance_user'), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    
    user = db.relationship('User', backref=db.backref('initial_balance', lazy=True))

class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    modules = db.Column(db.JSON, default=list)
    email_notifications = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('preferences', lazy=True))

class ReceiptDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    vendor_name = db.Column(db.String(100), nullable=False)
    tax = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    
    items = db.relationship('ReceiptItem', backref='receipt', cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('receipts', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'currency': self.currency,
            'vendor_name': self.vendor_name,
            'receipt_items': [item.to_dict() for item in self.items],
            'tax': self.tax,
            'total': self.total,
            'image_url': self.image_url
        }

class ReceiptItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt_detail.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    item_cost = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'item_name': self.item_name,
            'item_cost': self.item_cost
        }