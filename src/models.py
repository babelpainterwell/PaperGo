import os
from sqlalchemy import Column, String, create_engine, ForeignKey, Table, Integer
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import dateutil.parser
import babel
from flask_marshmallow import Marshmallow


db = SQLAlchemy()
ma = Marshmallow()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_path = os.environ['DATABASE_PATH']
    if database_path.startswith("postgres://"):
      database_path = database_path.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    # ma.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()
    # db.create_all()



class Paper(db.Model):
  __tablename__ = 'Paper'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String, nullable=False)
  abstract = db.Column(db.Text)
  publish_date = db.Column(db.DateTime)
  link = db.Column(db.String, nullable=False)

  def __init__(self, title, link, abstract='', publish_date=None):
     self.title = title 
     self.link = link
     self.abstract = abstract
     self.publish_date = publish_date
    

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      'abstract': self.abstract,
      'publish_date': self.publish_date,
      'link': self.link}
  
  def insert(self):
    try:
        db.session.add(self)
        db.session.commit()
    except:
        db.session.rollback()
        raise


  def delete(self):
    try:
        db.session.delete(self)
        db.session.commit()
    except:
        db.session.rollback()
        raise


  def update(self):
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise



class User(db.Model):
  __tablename__ = 'User'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False)
  institution = db.Column(db.String, nullable=False)
  profile_description  = db.Column(db.String, nullable=False)
  discoveries = db.relationship('Discovery', backref='user', lazy='joined')

  def __init__(self, email, password, name, institution, profile_description):
     self.email = email
     self.password = password
     self.name = name 
     self.institution = institution
     self.profile_description = profile_description
  

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'email': self.email,
      'institution': self.institution,
      'story': self.profile_description }
  
  def insert(self):
    try:
        db.session.add(self)
        db.session.commit()
    except:
        db.session.rollback()
        raise


  def delete(self):
    try:
        db.session.delete(self)
        db.session.commit()
    except:
        db.session.rollback()
        raise


  def update(self):
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


# only used for expanding the paper repo 
class Discovery(db.Model):
  __tablename__ = 'Discovery'
  id = db.Column(db.Integer, primary_key=True)
  date_posted = db.Column(db.DateTime, default=datetime.now)
  caption = db.Column(db.Text, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
  paper_id = db.Column(db.Integer, db.ForeignKey('Paper.id'), nullable=False)
  paper = db.relationship('Paper', backref='discoveries', lazy='joined')

  def __init__(self, caption, user_id, paper_id):
     self.caption = caption
     self.user_id = user_id
     self.paper_id = paper_id

  def format(self):
    try:
        user_name = self.user.name if self.user else None
        formatted_paper = self.paper.format() if self.paper else None
        
        return {
            'id': self.id,
            'date_posted': self.date_posted,
            'caption': self.caption,
            'paper': formatted_paper,
            'user_name': user_name
        }
    except AttributeError:
        return {
            'id': self.id,
            'error': 'Associated data is missing or incomplete.'
        }

  def insert(self):
    try:
        db.session.add(self)
        db.session.commit()
    except:
        db.session.rollback()
        raise


  def delete(self):
    try:
        db.session.delete(self)
        db.session.commit()
    except:
        db.session.rollback()
        raise


  def update(self):
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

class DiscoverySchema(ma.Schema):
   class Meta:
      fields = ('id', 'date_posted', 'caption')



