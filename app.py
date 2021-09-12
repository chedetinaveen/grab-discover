from flask import Flask, jsonify, render_template, send_from_directory, request
from apispec_webframeworks.flask import FlaskPlugin
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
import os
from db import db_init, db
from werkzeug.utils import secure_filename
from models import Merchant, Media, Post
import boto3
from dto import *
import uuid


app = Flask(__name__, template_folder='swagger/templates')


db_url = os.getenv('DATABASE_URL')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

s3 = boto3.client('s3', aws_access_key_id=os.getenv('S3_KEY'),
                  aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'))

db_init(app)


@app.route('/merchant/upload', methods=['POST'])
def media_upload():
    pic = request.files['file']
    if not pic:
        return 'file not uploaded', 400
    filename = secure_filename(pic.filename)
    unique_path = uuid.uuid4().hex
    s3.put_object(Body=pic.read(), Bucket=os.getenv(
        'S3_BUCKET'), Key=unique_path+'/'+filename)
    media = Media(uuid=unique_path, name=filename, mimetype=pic.mimetype)
    db.session.add(media)
    db.session.commit()
    return {'id': media.id}, 200


spec = APISpec(
    title='grab-discover-api-swagger-doc',
    version='1.0.0',
    openapi_version='3.0.3',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route("/")
@app.route('/docs')
@app.route('/docs/<path:path>')
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs', domain=os.getenv('SWAGGER_HOST'))
    else:
        return send_from_directory('./swagger/static', path)


@app.route('/api/swagger.json')
def create_swagger_spec():
    return jsonify(spec.to_dict())


@app.route('/merchant', methods=['POST'])
def create_merchant():
    """ Create a Merchant
        ---
        post:
            summary: create merchant
            description: Create merchant
            tags:
                - Merchant
            requestBody:
                required: true
                content:
                    application/json:
                        schema: CreateMerchantSchema


            responses:
                200:
                    description: merchant created
                    content:
                        application/json:
                            schema: CreateMerchantResponseSchema

                400:
                    description: invalid request
    """
    if not request.is_json:
        return 'Invalid Request', 400
    req = request.get_json()
    merchant = Merchant(name=req['name'], logo_id=req['logo_id'])
    db.session.add(merchant)
    db.session.commit()
    return {'id': merchant.id}, 200


@app.route('/merchant/<int:id>', methods=['GET'])
def get_merchant(id):
    """ Get Merchant
        ---
        get:
            summary: get merchant details
            description: Get Merchant by id
            tags:
                - Merchant
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id

            responses:
                200:
                    description: merchant details
                    content:
                        application/json:
                            schema: GetMerchantResponseSchema

                404:
                    description: not found
    """
    merchant = Merchant.query.get_or_404(id)
    if not merchant:
        return 'invalid id', 404
    media = Media.query.get_or_404(merchant.logo_id)
    return jsonify({'name': merchant.name, 'logo_url': media.get_url(os.getenv('S3_BUCKET'), os.getenv('S3_REGION'))}), 200


@app.route('/merchant/<int:id>', methods=['PUT'])
def update_merchant(id):
    """ Update Merchant
        ---
        put:
            summary: update merchant details
            description: Update Merchant by id
            tags:
                - Merchant
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id
            requestBody:
                required: true
                content:
                    application/json:
                        schema: UpdateMerchantSchema

            responses:
                204:
                    description: merchant details updated

                404:
                    description: merchant not found
    """
    merchant = Merchant.query.get_or_404(id)
    if not merchant:
        return 'invalid id', 404
    req = request.get_json()
    merchant.name = req['name']
    merchant.logo_id = req['logo_id']
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:id>', methods=['DELETE'])
def delete_merchant(id):
    """ Delete Merchant
        ---
        delete:
            summary: delete merchant
            description: Delete Merchant by id
            tags:
                - Merchant
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id

            responses:
                204:
                    description: merchant is deleted

                404:
                    description: merchant not found
    """
    merchant = Merchant.query.get_or_404(id)
    if not merchant:
        return 'invalid id', 404
    db.session.delete(merchant)
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:id>/post', methods=['POST'])
def create_post(id):
    """ Create Post
        ---
        post:
            summary: create post by merchant
            description: Create post
            tags:
                - Post
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id
            requestBody:
                required: true
                content:
                    application/json:
                        schema: CreatePostRequestSchema


            responses:
                200:
                    description: post created
                    content:
                        application/json:
                            schema: CreatePostResponseSchema

                400:
                    description: bad request
    """
    if not request.is_json:
        return 'Invalid Request', 400
    merchant = Merchant.query.get_or_404(id)
    req = request.get_json()
    post = Post(title=req['title'], media_id=req['media_id'],
                user_id=merchant.id)
    db.session.add(post)
    db.session.commit()
    return {'id': post.id}, 200


@app.route('/merchant/<int:id>/post/<int:post_id>', methods=['GET'])
def get_merchant_post(id, post_id):
    """ Get Post Details
        ---
        get:
            summary: get post details
            description: Get post details
            tags:
                - Post
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id
                - in: path
                  name: post_id
                  required: true
                  schema:
                    type: integer
                  description: post id

            responses:
                200:
                    description: post details
                    content:
                        application/json:
                            schema: GetPostResponseSchema

                404:
                    description: post not found
    """
    post = Post.query.get(post_id)
    media = Media.query.get_or_404(post.media_id)
    return {'id': post.id, 'title': post.title, 'media_url': media.get_url(os.getenv('S3_BUCKET'), os.getenv('S3_REGION')), 'date_posted': post.date_posted.isoformat()}, 200


@app.route('/merchant/<int:id>/posts', methods=['GET'])
def list_merchant_posts(id):
    """ List all Posts by merchant
        ---
        get:
            summary: list all posts by merchant
            description: list all posts
            tags:
                - Post
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id

            responses:
                200:
                    description: post details
                    content:
                        application/json:
                            schema: ListPostResponsesSchema

                404:
                    description: post not found
    """
    merchant = Merchant.query.get_or_404(id)
    posts = Post.query.filter_by(user_id=merchant.id).all()
    response = []
    for post in posts:
        media = Media.query.get_or_404(post.media_id)
        response.append({'id': post.id, 'title': post.title, 'media_url': media.get_url(os.getenv(
            'S3_BUCKET'), os.getenv('S3_REGION')), 'date_posted': post.date_posted.isoformat()})
    return {'posts': response}, 200


with app.test_request_context():
    spec.path(view=create_merchant)
    spec.path(view=get_merchant)
    spec.path(view=update_merchant)
    spec.path(view=delete_merchant)
    spec.path(view=create_post)
    spec.path(view=get_merchant_post)
    spec.path(view=list_merchant_posts)


if __name__ == '__main__':
    app.run(debug=True)
