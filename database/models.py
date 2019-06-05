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


###############################################

class UndesiredSubsequences(db.Model):
    __tablename__ = 'undesiredsubsequences'
    id = db.Column(db.Integer, primary_key=True)
    sequence = db.Column(db.String(512), nullable=False)
    error_prob = db.Column(db.FLOAT, nullable=False, default=0.0)
    created = db.Column(db.Integer, default=timestamp)
    validated = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(512))
    owner_id = db.Column(db.Integer, ForeignKey('User.user_id'))

    def __repr__(self):
        return '<UndesiredSubsequences(id={}, owner={}, sequence={}, error_prob={}, created={}, validated={}>'.format(
            self.id, self.owner_id, self.sequence, self.error_prob, self.created, self.validated)


###############################################

class Apikey(db.Model):
    __tablename__ = 'Apikey'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.Integer, default=timestamp, onupdate=timestamp)
    apikey = db.Column(db.String(64), index=True, unique=True)
    owner_id = db.Column(db.Integer, ForeignKey('User.user_id'))
    apikey_user_id_fk = db.relationship('User', backref=backref("User", uselist=False))

    def __repr__(self):
        return '<Apikey(id={}, owner={}) = {}>'.format(self.id, self.owner_id, self.apikey)


###############################################

class ErrorProbability(db.Model):
    __tablename__ = 'error_probability'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64))
    jsonblob = db.Column(db.JSON)
    validated = db.Column(db.Boolean, default=False, nullable=False)
    created = db.Column(db.Integer, default=timestamp)  # , onupdate=timestamp
    user_id = db.Column(db.Integer, ForeignKey('User.user_id'))

    # error_probability_user_user_id_fk = db.relationship('User', backref=backref("User", uselist=False))

    def __repr__(self):
        return '<ErrorProbability(id={}, owner={}) = {}>'.format(self.id, self.user_id, self.jsonblob)

    @staticmethod
    def serialize(ob, owner_id=None):
        tmp = {
            'id': ob.id,
            'name': ob.name,
            'type': ob.type,
            'jsonblob': ob.jsonblob,
            'validated': ob.validated,
            'created': ob.created,
            'user_id': ob.user_id,
        }
        if owner_id is not None:
            tmp['isowner'] = owner_id == ob.user_id
        return tmp
###############################################
