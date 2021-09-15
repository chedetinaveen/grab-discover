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


class UpdatePostRequestSchema(Schema):
    title = fields.Str()
    media_id = fields.Int()


class GetPostResponseSchema(Schema):
    id = fields.Int()
    media_url = fields.Str()
    media_mimetype = fields.Str()
    title = fields.Str()
    date_posted = fields.Str()
    logo_url = fields.Str()
    logo_mimetype = fields.Str()
    merchant_name = fields.Str()


class ListPostResponsesSchema(Schema):
    posts = fields.List(fields.Nested(GetPostResponseSchema))


class UploadMediaResponseSchema(Schema):
    id = fields.Int()


class GetDiscoverResponseSchema(Schema):
    id = fields.Int()
    merchant_name = fields.Str()
    logo_url = fields.Str()
    logo_mimetype = fields.Str()
    title = fields.Str()
    media_url = fields.Str()
    media_mimetype = fields.Str()
    likes = fields.Int()
    orders = fields.Int()


class ListDiscoverResponseSchema(Schema):
    posts = fields.List(fields.Nested(GetDiscoverResponseSchema))


class CreateUserSchema(Schema):
    profile_id = fields.Int()
    name = fields.Str()


class CreateUserResponseSchema(Schema):
    id = fields.Int()


class UpdateUserSchema(Schema):
    name = fields.Str()
    profile_id = fields.Str()
