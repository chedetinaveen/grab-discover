from flask import Flask, jsonify, render_template, send_from_directory, request
from apispec_webframeworks.flask import FlaskPlugin
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
import os
from db import db_init, db
from werkzeug.utils import secure_filename
from models import Merchant, Media, Post, User, Item, Boost
import boto3
from dto import *
import uuid
import datetime
from flask_cors import CORS, cross_origin


app = Flask(__name__, template_folder='swagger/templates')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db_url = os.getenv('DATABASE_URL')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

s3 = boto3.client('s3', aws_access_key_id=os.getenv('S3_KEY'),
                  aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'))

db_init(app)


@app.route('/media/upload', methods=['POST'])
@cross_origin()
def media_upload():
    """ Upload Media
        ---
        post:
            summary: upload images or video
            description: Upload Media
            tags:
                - Media
            requestBody:
                content:
                    multipart/form-data:
                        schema:
                            type: object
                            properties:
                                file:
                                    type: string
                                    format: binary
                                    required: true

            responses:
                200:
                    description: media id of the upload
                    content:
                        application/json:
                            schema: UploadMediaResponseSchema

                400:
                    description: invalid request
    """
    if not ('file' in request.files):
        return 'file not uploaded', 400
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
    return {'id': media.id, 'media_url': media.get_url(os.getenv('S3_BUCKET'), os.getenv('S3_REGION'))}, 200


spec = APISpec(
    title='grab-discover-api-swagger-doc',
    version='1.0.0',
    openapi_version='3.0.3',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route("/")
@app.route('/docs')
@app.route('/docs/<path:path>')
@cross_origin()
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs', domain=os.getenv('SWAGGER_HOST'))
    else:
        return send_from_directory('./swagger/static', path)


@app.route('/api/swagger.json')
@cross_origin()
def create_swagger_spec():
    return jsonify(spec.to_dict())


@app.route('/merchant', methods=['POST'])
@cross_origin()
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
@cross_origin()
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
@cross_origin()
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
@cross_origin()
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
@cross_origin()
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
                user_id=merchant.id, items=req['items'])
    db.session.add(post)
    db.session.commit()
    return {'id': post.id}, 200


@app.route('/merchant/<int:id>/post/<int:post_id>', methods=['PUT'])
@cross_origin()
def update_post(id, post_id):
    """ Update Post
        ---
        put:
            summary: update post by merchant
            description: Update post
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
                  description: id of the post
            requestBody:
                required: true
                content:
                    application/json:
                        schema: UpdatePostRequestSchema


            responses:
                204:
                    description: post updated

                400:
                    description: bad request
    """
    if not request.is_json:
        return 'Invalid Request', 400
    Merchant.query.get_or_404(id)
    post = Post.query.get_or_404(post_id)
    req = request.get_json()
    post.title = req['title']
    post.media_id = req['media_id']
    post.items = req['items']
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:id>/post/<int:post_id>', methods=['DELETE'])
@cross_origin()
def delete_post(id, post_id):
    """ Delete Post
        ---
        delete:
            summary: delete post by merchant
            description: Delete post
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
                  description: id of the post

            responses:
                204:
                    description: post deleted

                404:
                    description: post not found
    """
    Merchant.query.get_or_404(id)
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return '', 204


def get_items(items):
    if items is None:
        return []
    itemDetails = []
    for i in items:
        item = Item.query.get(i)
        if not item:
            continue
        media_item = Media.query.get_or_404(item.media_id)
        itemDetails.append({'id': item.id, 'name': item.name, 'media_mimetype': media_item.mimetype, 'media_url': media_item.get_url(os.getenv(
            'S3_BUCKET'), os.getenv('S3_REGION')), 'price': item.price, 'currency': item.currency, 'description': item.description, 'price': item.price, 'currency': item.currency})
    return itemDetails


@app.route('/merchant/<int:id>/post/<int:post_id>', methods=['GET'])
@cross_origin()
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
    merchant = Merchant.query.get_or_404(post.user_id)
    logo = Media.query.get_or_404(merchant.logo_id)
    items = get_items(post.items)
    currentTime = datetime.datetime.utcnow()
    boost = Boost.query.filter(
        Boost.end_time > currentTime).filter_by(post_id=post.id).first()
    isBoosted = False
    if boost is not None and boost.id > 0:
        isBoosted = True
    return {'id': post.id, 'title': post.title, 'media_url': media.get_url(os.getenv('S3_BUCKET'), os.getenv('S3_REGION')), 'date_posted': post.date_posted.isoformat(), 'merchant_name': merchant.name, 'logo_url': logo.get_url(os.getenv(
        'S3_BUCKET'), os.getenv('S3_REGION')), 'logo_mimetype': logo.mimetype, 'media_mimetype': media.mimetype, 'items': items, 'is_boosted': isBoosted}, 200


@app.route('/merchant/<int:id>/posts', methods=['GET'])
@cross_origin()
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
    posts.sort(key=lambda x: (x.date_posted
               - datetime.datetime(1970, 1, 1)).total_seconds(), reverse=True)
    logo = Media.query.get_or_404(merchant.logo_id)
    response = []
    for post in posts:
        media = Media.query.get_or_404(post.media_id)

        response.append({'items': get_items(post.items), 'id': post.id, 'title': post.title, 'media_url': media.get_url(os.getenv(
            'S3_BUCKET'), os.getenv('S3_REGION')), 'date_posted': post.date_posted.isoformat(), 'merchant_name': merchant.name, 'logo_url': logo.get_url(os.getenv(
                'S3_BUCKET'), os.getenv('S3_REGION')), 'logo_mimetype': logo.mimetype, 'media_mimetype': media.mimetype})
    return {'posts': response}, 200


@app.route('/discover', methods=['GET'])
@cross_origin()
def get_discover():
    """ Discover the feed
        ---
        get:
            summary: list all posts in discover
            description: list all posts
            tags:
                - Discover

            responses:
                200:
                    description: post details
                    content:
                        application/json:
                            schema: ListDiscoverResponseSchema

                404:
                    description: post not found
    """
    posts = Post.query.all()
    posts.sort(key=lambda x: (x.date_posted
               - datetime.datetime(1970, 1, 1)).total_seconds(), reverse=True)
    response = []
    for post in posts:
        media = Media.query.get_or_404(post.media_id)
        merchant = Merchant.query.get_or_404(post.user_id)
        logo = Media.query.get_or_404(merchant.logo_id)

        response.append({'items': get_items(post.items), 'id': post.id, 'title': post.title, 'media_url': media.get_url(os.getenv(
            'S3_BUCKET'), os.getenv('S3_REGION')), 'date_posted': post.date_posted.isoformat(), 'merchant_name': merchant.name, 'logo_url': logo.get_url(os.getenv(
                'S3_BUCKET'), os.getenv('S3_REGION')), 'logo_mimetype': logo.mimetype, 'media_mimetype': media.mimetype, 'merchant_id': merchant.id})
    return {'posts': response}, 200


@app.route('/user', methods=['POST'])
@cross_origin()
def create_user():
    """ Create User
        ---
        post:
            summary: create user
            description: Create user
            tags:
                - User
            requestBody:
                required: true
                content:
                    application/json:
                        schema: CreateUserSchema


            responses:
                200:
                    description: user created
                    content:
                        application/json:
                            schema: CreateUserResponseSchema

                400:
                    description: invalid request
    """
    if not request.is_json:
        return 'Invalid Request', 400
    req = request.get_json()
    user = User(name=req['name'], media_id=req['profile_id'])
    db.session.add(user)
    db.session.commit()
    return {'id': user.id}, 200


@app.route('/user/<int:id>', methods=['PUT'])
@cross_origin()
def update_user(id):
    """ Update User
        ---
        put:
            summary: update user details
            description: Update user by id
            tags:
                - User
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: user id
            requestBody:
                required: true
                content:
                    application/json:
                        schema: UpdateUserSchema

            responses:
                204:
                    description: user details updated

                404:
                    description: user not found
    """
    user = User.query.get_or_404(id)
    req = request.get_json()
    user.name = req['name']
    user.media_id = req['profile_id']
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:id>/item', methods=['POST'])
@cross_origin()
def create_item(id):
    """ Create Menu Item
        ---
        post:
            summary: create menu item
            description: create menu item
            tags:
                - Menu
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
                        schema: CreateItemSchema


            responses:
                200:
                    description: item created
                    content:
                        application/json:
                            schema: CreateItemResponseSchema

                400:
                    description: invalid request
    """
    if not request.is_json:
        return 'Invalid Request', 400
    req = request.get_json()
    Merchant.query.get_or_404(id)
    item = Item(name=req['name'], media_id=req['media_id'],
                merchant_id=id, price=req['price'], currency=req['currency'], description=req['description'])
    db.session.add(item)
    db.session.commit()
    return {'id': item.id}, 200


@app.route('/merchant/<int:id>/item/<int:item_id>', methods=['PUT'])
@cross_origin()
def update_item(id, item_id):
    """ Update Menu Item
        ---
        put:
            summary: update menu item
            description: update menu item
            tags:
                - Menu
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id
                - in: path
                  name: item_id
                  required: true
                  schema:
                    type: integer
                  description: item id to be updated
            requestBody:
                required: true
                content:
                    application/json:
                        schema: UpdateItemSchema


            responses:
                204:
                    description: item updated

                400:
                    description: invalid request

                404:
                    description: item not found
    """
    if not request.is_json:
        return 'Invalid Request', 400
    req = request.get_json()
    Merchant.query.get_or_404(id)
    item = Item.query.get_or_404(item_id)
    item.name = req['name']
    item.media_id = req['media_id']
    item.price = req['price']
    item.currency = req['currency']
    item.description = req['description']
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:id>/item/<int:item_id>', methods=['GET'])
@cross_origin()
def get_item(id, item_id):
    """ Get Menu Item
        ---
        get:
            summary: get menu item
            description: get menu item
            tags:
                - Menu
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id
                - in: path
                  name: item_id
                  required: true
                  schema:
                    type: integer
                  description: item id

            responses:
                204:
                    description: item updated
                    content:
                        application/json:
                            schema: GetItemResponseSchema

                404:
                    description: item not found
    """
    Merchant.query.get_or_404(id)
    item = Item.query.get_or_404(item_id)
    media = Media.query.get_or_404(item.media_id)
    return {'id': item.id, 'name': item.name, 'media_mimetype': media.mimetype, 'media_url': media.get_url(os.getenv('S3_BUCKET'), os.getenv('S3_REGION')), 'price': item.price, 'currency': item.currency, 'description': item.description}, 200


@app.route('/merchant/<int:id>/menu', methods=['GET'])
@cross_origin()
def get_menu(id):
    """ Get Menu
        ---
        get:
            summary: get menu
            description: get menu
            tags:
                - Menu
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: merchant id
            responses:
                200:
                    description: merchant menu
                    content:
                        application/json:
                            schema: ListMenuResponseSchema

                400:
                    description: invalid request
    """
    Merchant.query.get_or_404(id)
    items = Item.query.filter_by(merchant_id=id).all()
    items.sort(key=lambda x: x.name)
    response = []
    for item in items:
        media = Media.query.get_or_404(item.media_id)
        response.append({'id': item.id, 'name': item.name, 'media_mimetype': media.mimetype,
                        'media_url': media.get_url(os.getenv('S3_BUCKET'), os.getenv('S3_REGION')), 'price': item.price, 'currency': item.currency, 'description': item.description})
    return {'items': response}, 200


@app.route('/post/<int:id>/boost', methods=['POST'])
@cross_origin()
def boost_post(id):
    """ Boost Post
        ---
        post:
            summary: boost a post
            description: boost a post
            tags:
                - Boost
            parameters:
                - in: path
                  name: id
                  required: true
                  schema:
                    type: integer
                  description: post id
            requestBody:
                required: true
                content:
                    application/json:
                        schema: BoostRequestSchema
            responses:
                200:
                    description: boost status
                    content:
                        application/json:
                            schema: BoostResponseSchema

                400:
                    description: invalid request
    """
    if not request.is_json:
        return 'invalid request', 400
    req = request.get_json()
    currentTime = datetime.datetime.utcnow()
    endtime = currentTime + datetime.timedelta(days=req['days'])
    existingBoost = Boost.query.filter(Boost.end_time > currentTime).all()
    if existingBoost is not None and len(existingBoost) > 0:
        return '', 400
    Post.query.get_or_404(id)
    boost = Boost(post_id=id, end_time=endtime)
    db.session.add(boost)
    db.session.commit()
    return {'success': True}, 200


@app.route('/user/<int:id>/post/<int:post_id>', methods=['POST'])
@cross_origin()
def like(id, post_id):
    return '', 204


with app.test_request_context():
    spec.path(view=create_merchant)
    spec.path(view=get_merchant)
    spec.path(view=update_merchant)
    spec.path(view=delete_merchant)
    spec.path(view=create_post)
    spec.path(view=update_post)
    spec.path(view=delete_post)
    spec.path(view=get_merchant_post)
    spec.path(view=list_merchant_posts)
    spec.path(view=media_upload)
    spec.path(view=get_discover)
    spec.path(view=create_user)
    spec.path(view=update_user)
    spec.path(view=create_item)
    spec.path(view=update_item)
    spec.path(view=get_item)
    spec.path(view=get_menu)
    spec.path(view=boost_post)


if __name__ == '__main__':
    app.run(debug=True)
