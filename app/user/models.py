# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

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
from app.constants import (
    permissions,
    role_names
)


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.BigInteger)
    user = relationship("User", backref="roles")

    
    @classmethod
    def populate(cls):
            
        roles = {
            role_name.ANONYMOUS:(
                permission.ORDER |
                permission.PAY
            ),
            role_name.CUSTOMER:(
                permission.ORDER |
                permission.PAY |
                permission.COMMENT
            ),
            role_name.DELIVERYPERSON:(
                permission.BID |
                permission.ROUTES |
                permission.CUSTOMER_COMMENT
            ), 
            role_name.COOK: (
                permission.FOOD_QUALITY |
                permission.MENU |
                permission.PRICES 
            ),
            role_name.SALESPERSON: (
                permission.SUPPLIER
            ),
            role_name.MANAGER:(
                permission.COMMISSIONS |
                permission.PAY |
                permission.COMPLAINTS |
                permission.MANAGEMENT
            ),
            role_name.ADMIN:(
                permission.ORDER |
                permission.PAY |
                permission.ORDER |
                permission.PAY |
                permission.COMMENT |
                permission.BID |
                permission.ROUTES |
                permission.CUSTOMER_COMMENT | 
                permission.FOOD_QUALITY |
                permission.MENU |
                permission.PRICES |
                permission.SUPPLIER | 
                permission.COMMISSIONS |
                permission.PAY |
                permission.COMPLAINTS |
                permission.MANAGEMENT
            )

        }

        for name, value in roles.items():
            role = Roles.query.filter_by(name=name).first()
            if role is None:
                role = cls(name=name)
            role.permissions = value
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Roles %r>' % self.id

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
    password = Column(db.LargeBinary(128), nullable=True)
    phone_number = Column(db.String(25), nullable=True)
    address = Column(db.String(200), nullable=True)
    active = Column(db.Boolean(), default=False)
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id))
    stars = db.Column(db.Integer, default=0)
    salary = db.Column(db.Integer, default=0)
    commision = db.Column(db.Integer, default=10)
    credit_card = db.Column(db.Integer, nullable=True, default=None)
    cv = db.Column(db.Integer, nullable=True, default=None)
    ctype = db.Column(db.String(10), nullable=True, default='')


    def __init__(self,
                 username,
                 first_name,
                 middle_initial,
                 last_name,
                 email,
                 phone_number,
                 role_id,
                 password, 
                 address, 
                 active, 
                 stars,
                 salary,
                 commision, 
                 credit_card,
                 cv, 
                 ctype):
        self.username = username
        self.first_name = first_name
        self.middle_initial = middle_initial
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.role_id = role_id
        self.set_password(password, update_history=False)  # only update on password resets
        self.address = address
        self.active = active
        self.stars = stars
        self.salary = salary
        self.commision = commision
        self.credit_card = credit_card
        self.cv = cv
        self.ctype=ctype


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
    def has_invalid_password(self):

        """
        Returns whether the user's password is expired or is the default password (True) or not (False).
        """
        if current_app.config['USE_LOCAL_AUTH']:
            return datetime.utcnow() > self.expiration_date or self.check_password(current_app.config['DEFAULT_PASSWORD'])
        return False


    def is_new_password(self, password):
        """
        Returns whether the supplied password is not the same as the current
        or previous passwords (True) or not (False).
        """
        existing_passwords = list(filter(None, [self.password] + [h.password for h in self.history.all()]))
        return not existing_passwords or all(not check_password_hash(p, password) for p in existing_passwords)


    def set_password(self, password, update_history=True):
        if self.is_new_password(password):
            if update_history:
                # update previous passwords
                if self.history.count() >= self.MAX_PREV_PASS:
                    # remove oldest password
                    self.history.filter_by(  # can't call delete() when using order_by()
                        id=self.history.order_by(History.timestamp.asc()).first().id
                    ).delete()
                db.session.add(History(self.id, self.password))

            self.expiration_date = datetime.utcnow() + timedelta(days=self.DAYS_UNTIL_EXPIRATION)
            self.password = generate_password_hash(password)

            db.session.commit()


    def update_password(self, current_password, new_password):
        if self.check_password(current_password):
            self.set_password(new_password)


    def check_password(self, password):
        return check_password_hash(self.password, password)


    @classmethod
    def populate(cls):
        roles_dict = {}
        roles = Roles.query.all()
        for role in roles:
            roles_dict[role.name] = role.id

        with open(current_app.config['USER_DATA'], 'r') as data:
            dictreader = csv.DictReader(data)

            for row in dictreader:
                user = cls(
                    first_name=row['first_name'],
                    middle_initial=row['middle_initial'],
                    last_name=row['last_name'],
                    email=row['email'],
                    username=row['username'],
                    phone_number=row['phone_number'],
                    role_id=roles_dict[row['role']],
                    password=current_app.config['DEFAULT_PASSWORD'],
                    address=row['address'],
                    active=row['active'],
                    stars=row['stars'],
                    salary=row['salary'],
                    commision=row['commision'],
                    credit_card=row['credit_card'],
                    cv=row['cv'], 
                    ctype=row['ctype']
                )
                db.session.add(user)
        db.session.commit()

    @staticmethod
    def generate_fake(count=20):
        """
        Used to generate fake users.
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint

        import forgery_py

        seed()
        
        for i in range(count):
            first = forgery_py.name.first_name()
            middle = forgery_py.middle_initial()
            last = forgery_py.name.last_name()
            username = first + str(randint(0,99))
            # forgery_py.address.state_abbrev()
            # + ', ' + forgery_py.address.zip_code())
            e = (first[:1] + last + "@gmail.com").lower()
            u = User(
                email=e,
                password=forgery_py.lorem_ipsum.word(),  # change to set a universal password for QA testing
                first_name=first,
                last_name=last,
                middle_initial=middle,
                username=username,
                phone_number=forgery_py.address.phone(),
                active=True
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<User({username!r})>".format(username=self.username)
