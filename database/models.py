import time

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
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
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    ###############################################
    def get_token(self, secret):
        s = URLSafeTimedSerializer(secret)
        return s.dumps({'user_id': self.user_id})  # .decode('utf-8')

    @staticmethod
    def verify_token(token, secret, expiration=1800):
        s = URLSafeTimedSerializer(secret)
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

    @staticmethod
    def serialize(ob):
        tmp = {'id': ob.user_id, 'email': ob.email, 'created': ob.created, 'validated': ob.validated,
               'is_admin': ob.is_admin}
        return tmp


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
    awaits_validation = db.Column(db.Boolean, default=False, nullable=False)
    validation_desc = db.Column(db.String(512))

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
    awaits_validation = db.Column(db.Boolean, default=False, nullable=False)
    validation_desc = db.Column(db.String(512))

    def __repr__(self):
        return '<ErrorProbability(id={}, owner={}) = {}>'.format(self.id, self.user_id, self.jsonblob)

    @staticmethod
    def serialize(ob, owner_id=None):
        tmp = {'id': ob.id, 'name': ob.name, 'type': ob.type, 'jsonblob': ob.jsonblob, 'validated': ob.validated,
               'created': ob.created, 'user_id': ob.user_id, 'awaits_validation': ob.awaits_validation,
               'isowner': owner_id == ob.user_id if owner_id is not None else False}
        return tmp


###############################################


class SequencingErrorRates(db.Model):
    __tablename__ = 'seq_err_rates'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, ForeignKey('meth_categories.id'), nullable=False)
    err_data = db.Column(db.JSON)
    user_id = db.Column(db.Integer, ForeignKey('User.user_id'))
    validated = db.Column(db.Boolean, default=False, nullable=False)
    err_attributes = db.Column(db.JSON)
    name = db.Column(db.TEXT)
    awaits_validation = db.Column(db.Boolean, default=False, nullable=False)
    validation_desc = db.Column(db.String(512))

    def __repr__(self):
        return '<SequencingErrorRates(id={}, method_id={}, correction_id={}, err_data={}'.format(
            self.id, self.method, self.correction_id, self.err_data)

    def as_dict(self):
        return dict((col, getattr(self, col)) for col in
                    self.__table__.columns.keys())


###############################################


class SynthesisErrorRates(db.Model):
    __tablename__ = 'synth_err_rates'
    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, ForeignKey('meth_categories.id'), nullable=False)
    err_data = db.Column(db.JSON)
    user_id = db.Column(db.Integer, ForeignKey('User.user_id'))
    validated = db.Column(db.Boolean, default=False, nullable=False)
    err_attributes = db.Column(db.JSON)
    name = db.Column(db.TEXT)
    awaits_validation = db.Column(db.Boolean, default=False, nullable=False)
    validation_desc = db.Column(db.String(512))

    def __repr__(self):
        return '<SequencingErrorRates(id={}, method_id={}, correction_id={}, err_data={}'.format(
            self.id, self.method, self.correction_id, self.err_data)

    def as_dict(self):
        return dict((col, getattr(self, col)) for col in
                    self.__table__.columns.keys())


###############################################


class MethodCategories(db.Model):
    __tablename__ = 'meth_categories'
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SequencingErrorAttributes(id={}, method_id={}, correction_id={}, err_data={}'.format(
            self.id, self.err_, self.correction_id, self.err_data)

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in
                self.__table__.columns}  # {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

###############################################
