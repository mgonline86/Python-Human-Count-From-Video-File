import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Connect to the database
database_filename = "Database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(
    os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String, nullable=False)
    logged = db.Column(db.Boolean, default=False)
    videos = db.relationship('Video', backref='video_user', lazy=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    size = db.Column(db.Integer, nullable=False)
    humans = db.Column(db.Integer, nullable=False)
    pent = db.Column(db.Integer, nullable=False)
    not_pent = db.Column(db.Integer, nullable=False)
    percent = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
