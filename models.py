
from db import db
from datetime import datetime


class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, unique=True, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)


class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False, unique=True)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"Merchant('{self.id}', '{self.name}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'merchant.id'), nullable=False)
    title = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Post('{self.id}', '{self.media}',  '{self.date_posted}')"
