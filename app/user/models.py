# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from flask_login import UserMixin

from app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from app.extensions import bcrypt
from app.constants import permission, role_names
from werkzeug.security import generate_password_hash, check_password_hash


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.BigInteger)

    @classmethod
    def populate(cls):

        roles = {
            role_names.ANONYMOUS: (permission.ORDER | permission.PAY),
            role_names.CUSTOMER: (
                permission.ORDER | permission.PAY | permission.COMMENT
            ),
            role_names.DELIVERYPERSON: (
                permission.BID | permission.ROUTES | permission.CUSTOMER_COMMENT
            ),
            role_names.COOK: (
                permission.FOOD_QUALITY | permission.MENU | permission.PRICES
            ),
            role_names.SALESPERSON: (permission.SUPPLIER),
            role_names.MANAGER: (
                permission.COMMISSIONS
                | permission.PAY
                | permission.COMPLAINTS
                | permission.MANAGEMENT
            ),
            role_names.ADMIN: (
                permission.ORDER
                | permission.PAY
                | permission.ORDER
                | permission.PAY
                | permission.COMMENT
                | permission.BID
                | permission.ROUTES
                | permission.CUSTOMER_COMMENT
                | permission.FOOD_QUALITY
                | permission.MENU
                | permission.PRICES
                | permission.SUPPLIER
                | permission.COMMISSIONS
                | permission.PAY
                | permission.COMPLAINTS
                | permission.MANAGEMENT
            ),
        }

        for name, value in roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = cls(name=name)
            role.permissions = value
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.id

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<Role({name})>".format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    first_name = Column(db.String(30), nullable=True)
    middle_initial = Column(db.String(2), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(128))
    phone_number = Column(db.String(25), nullable=True)
    address = Column(db.String(200), nullable=True)
    active = Column(db.Boolean(), default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    stars = db.Column(db.Integer, default=0)
    salary = db.Column(db.Integer, default=0)
    commision = db.Column(db.Integer, default=10)
    credit_card = db.Column(db.Integer, nullable=True, default=None)
    cv = db.Column(db.Integer, nullable=True, default=None)
    ctype = db.Column(db.String(10), nullable=True, default="")

    def __init__(
        self,
        username,
        first_name,
        middle_initial,
        last_name,
        email,
        phone_number,
        role_id,
        password_hash,
        address,
        active,
        stars,
        salary,
        commision,
        credit_card,
        cv,
        ctype,
    ):
        self.username = username
        self.first_name = first_name
        self.middle_initial = middle_initial
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.role_id = role_id
        self.password_hash = password(password)
        self.address = address
        self.active = active
        self.stars = stars
        self.salary = salary
        self.commision = commision
        self.credit_card = credit_card
        self.cv = cv
        self.ctype = ctype

    @property
    def name(self):
        """
        Property to return a User's full name, including middle initial if applicable.
        :return:
        """
        if self.middle_initial:
            return self.first_name + " " + self.middle_initial + " " + self.last_name
        return self.first_name + " " + self.last_name

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """
        Creates and stores password hash.
        :param password: String to hash.
        :return: None.
        """
        self.password_hash = generate_password_hash(password)


    # def set_password(self, password):
    #     u = User.query.filter_by(id=self.id).first()
    #     u.password = generate_password_hash(password)
    #     db.session.add(u)
    #     db.session.commit()

    def update_password(self, current_password, new_password):
        if self.check_password(current_password):
            self.set_password(new_password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        """
        Checks to see if a user has access to certain permissions.
        :param permissions: An int that specifies the permissions we are checking to see whether or not the user has.
        :return: True if user is authorized for the given permission, False otherwise.
        """
        return (
            self.role is not None
            and (self.role.permissions & permissions) == permissions
        )

    @staticmethod
    def generate_fake(count=20):
        """
        Used to generate fake users.
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint, choice
        import string
        import forgery_py

        seed()

        for i in range(count):
            first = forgery_py.name.first_name()
            middle = (choice(string.ascii_letters)).upper()
            last = forgery_py.name.last_name()
            username = first + str(randint(0, 99))
            whole_address = (
                forgery_py.address.street_address()
                + " "
                + forgery_py.address.city()
                + " "
                + forgery_py.address.state()
                + " "
                + forgery_py.address.zip_code()
            )
            e = (first[:1] + last + "@gmail.com").lower()
            u = User(
                username=username,
                email=e,
                first_name=first,
                middle_initial=middle,
                last_name=last,
                password="test12345",
                phone_number=forgery_py.address.phone(),
                role_id=0,
                address=whole_address,
                active=True,
                stars=0,
                salary=0,
                commision=0,
                credit_card=forgery_py.credit_card.number(),
                cv=randint(0, 999),
                ctype=forgery_py.credit_card.type(),
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<User({username!r})>".format(username=self.username)
