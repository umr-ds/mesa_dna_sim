import time

from flask import current_app
from itsdangerous import Serializer, TimedSerializer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import backref

from .db import db


def timestamp():
    """Return the current timestamp as an integer."""
    return int(time.time())


class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128), nullable=False)
    created = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    validated = db.Column(db.Boolean, default=False, nullable=False)

    ###############################################
    def get_token(self, secret):
        s = TimedSerializer(secret)
        return s.dumps({'user_id': self.user_id})  # .decode('utf-8')

    @staticmethod
    def verify_token(token, secret, expiration=1800):
        s = TimedSerializer(secret)
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return None
        user_id = data.get('user_id')
        if user_id:
            return User.query.get(user_id)
        return None

    ###############################################

    def get_password_reset_token(self):
        return self.get_token(current_app.config['SECRET_EMAIL_VALIDATION_KEY'])

    @staticmethod
    def verify_password_reset_token(token, expiration=1800):
        return User.verify_token(token, current_app.config['SECRET_EMAIL_VALIDATION_KEY'], expiration=expiration)

    def get_account_deletion_token(self):
        return self.get_token(current_app.config['SECRET_ACCOUNT_DELETION_VALIDATION_KEY'])

    @staticmethod
    def verify_account_deletion_token(token, expiration=500):
        return User.verify_token(token, current_app.config['SECRET_ACCOUNT_DELETION_VALIDATION_KEY'],
                                 expiration=expiration)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Apikey(db.Model):
    __tablename__ = 'Apikey'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    apikey = db.Column(db.String(64), index=True, unique=True)
    owner_id = db.Column(db.Integer, ForeignKey('User.user_id'))
    apikey_user_id_fk = db.relationship('User', backref=backref("User", uselist=False))

    def __repr__(self):
        return '<Apikey(id={}, owner={}) = {}>'.format(self.id, self.owner_id, self.apikey)
