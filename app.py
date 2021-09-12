from flask import Flask, jsonify, render_template, send_from_directory, request
from apispec_webframeworks.flask import FlaskPlugin
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
import os
from db import db_init, db
from werkzeug.utils import secure_filename
from models import Merchant, Img
import boto3
from dto import *


app = Flask(__name__, template_folder='swagger/templates')


db_url = os.getenv('DATABASE_URL')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

s3 = boto3.client('s3', aws_access_key_id=os.getenv('S3_KEY'),
                  aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'))

db_init(app)


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'file not uploaded', 400
    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    img = Img(img=pic.read(), mimetype=mimetype, name=filename)
    db.session.add(img)
    db.session.commit()
    return 'Img uploaded', 200


@app.route('/merchant/upload', methods=['POST'])
def video_upload():
    pic = request.files['file']
    if not pic:
        return 'file not uploaded', 400
    filename = secure_filename(pic.filename)
    s3.put_object(Body=pic.read(), Bucket=os.getenv('S3_BUCKET'), Key=filename)
    return 'Upload Success', 200


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
        return render_template('index.html', base_url='/docs')
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
            description: Create merchants
            requestBody:
                required: true
                content:
                    application/json:
                        schema: CreateMerchantSchema


            responses:
                204:
                    description: merchant created

                400:
                    description: invalid request
    """
    if not request.is_json:
        return 'Invalid Request', 400
    req = request.get_json()
    merchant = Merchant(name=req['name'], logo=req['logo'])
    db.session.add(merchant)
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:id>', methods=['GET'])
def get_merchant(id):
    """ Get Merchant
        ---
        get:
            description: Get Merchant by id
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
    return jsonify({'name': merchant.name, 'logo': merchant.logo}), 200


@app.route('/merchant/<int:id>', methods=['PUT'])
def update_merchant(id):
    """ Get Merchant
        ---
        put:
            description: Get Merchant by id
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
    merchant.logo = req['logo']
    db.session.commit()
    return '', 204


@app.route('/merchant/<int:merchant_id>', methods=['DELETE'])
def delete_merchant(merchant_id):
    merchant = Merchant.query.get_or_404(merchant_id)
    if not merchant:
        return 'invalid merchant_id', 404
    db.session.delete(merchant)
    db.session.commit()
    return '', 204


@ app.route('/merchant/post')
def merchant_post():
    return 'merchant post'


with app.test_request_context():
    spec.path(view=create_merchant)
    spec.path(view=get_merchant)
    spec.path(view=update_merchant)


if __name__ == '__main__':
    app.run(debug=True)
