
from db import db
from datetime import datetime


class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_id = db.Column(db.Integer, db.ForeignKey(
        'media.id'), nullable=False, default=1)
    name = db.Column(db.Text, nullable=False, unique=True)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"Merchant('{self.id}', '{self.name}')"


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    date_uploaded = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Media('{self.id}', '{self.uuid}', '{self.name}')"

    def get_url(self, bucket, region):
        return 'https://'+bucket+'.s3.'+region+'.amazonaws.com/'+self.uuid+'/'+self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'merchant.id'), nullable=False)
    title = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Post('{self.id}', '{self.media}',  '{self.date_posted}')"
        return f"Post('{self.id}', '{self.media}',  '{self.date_posted}')"
        return f"Post('{self.id}', '{self.media}',  '{self.date_posted}')"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
