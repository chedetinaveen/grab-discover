from marshmallow import Schema, fields


class CreateMerchantSchema(Schema):
    name = fields.Str()
    logo_id = fields.Int()


class CreateMerchantResponseSchema(Schema):
    id = fields.Int()


class GetMerchantResponseSchema(Schema):
    name = fields.Str()
    logo_url = fields.Str()


class UpdateMerchantSchema(Schema):
    name = fields.Str()
    logo_id = fields.Int()


class CreatePostRequestSchema(Schema):
    title = fields.Str()
    media_id = fields.Int()


class CreatePostResponseSchema(Schema):
    id = fields.Int()


class GetPostResponseSchema(Schema):
    id = fields.Int()
    media_url = fields.Str()
    title = fields.Str()
    date_posted = fields.Str()


class ListPostResponsesSchema(Schema):
    posts = fields.List(fields.Nested(GetPostResponseSchema))
