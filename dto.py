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
    items = fields.List(fields.Int())


class CreatePostResponseSchema(Schema):
    id = fields.Int()


class UpdatePostRequestSchema(Schema):
    title = fields.Str()
    media_id = fields.Int()
    items = fields.List(fields.Int())


class UploadMediaResponseSchema(Schema):
    id = fields.Int()
    media_url = fields.Str()


class CreateUserSchema(Schema):
    profile_id = fields.Int()
    name = fields.Str()


class CreateUserResponseSchema(Schema):
    id = fields.Int()


class UpdateUserSchema(Schema):
    name = fields.Str()
    profile_id = fields.Int()


class CreateItemSchema(Schema):
    name = fields.Str()
    media_id = fields.Int()
    price = fields.Int()
    description = fields.Str()
    currency = fields.Str()


class CreateItemResponseSchema(Schema):
    id = fields.Int()


class UpdateItemSchema(Schema):
    name = fields.Str()
    media_id = fields.Int()
    price = fields.Int()
    currency = fields.Str()
    description = fields.Str()


class GetItemResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    media_url = fields.Str()
    media_mimetype = fields.Str()
    currency = fields.Str()
    price = fields.Int()
    description = fields.Str()


class ListMenuResponseSchema(Schema):
    items = fields.List(fields.Nested(GetItemResponseSchema))


class GetPostResponseSchema(Schema):
    id = fields.Int()
    media_url = fields.Str()
    media_mimetype = fields.Str()
    title = fields.Str()
    date_posted = fields.Str()
    logo_url = fields.Str()
    logo_mimetype = fields.Str()
    merchant_name = fields.Str()
    items = fields.List(fields.Nested(GetItemResponseSchema))
    is_boosted = fields.Bool()
    likes = fields.Int()
    comments = fields.Int()


class ListPostResponsesSchema(Schema):
    posts = fields.List(fields.Nested(GetPostResponseSchema))


class GetDiscoverResponseSchema(Schema):
    id = fields.Int()
    merchant_name = fields.Str()
    logo_url = fields.Str()
    logo_mimetype = fields.Str()
    title = fields.Str()
    media_url = fields.Str()
    media_mimetype = fields.Str()
    is_boosted = fields.Bool()
    orders = fields.Int()
    likes = fields.Int()
    comments = fields.Int()
    is_liked = fields.Bool()
    merchant_id = fields.Int()
    items = fields.List(fields.Nested(GetItemResponseSchema))


class ListDiscoverResponseSchema(Schema):
    posts = fields.List(fields.Nested(GetDiscoverResponseSchema))


class BoostRequestSchema(Schema):
    days = fields.Int()


class BoostResponseSchema(Schema):
    success = fields.Bool()


class UpdateLikeRequestSchema(Schema):
    user_id = fields.Int()


class UpdateLikeResponseSchema(Schema):
    total_likes = fields.Int()
    is_liked = fields.Bool()


class CommentRequestSchema(Schema):
    user_id = fields.Int()
    content = fields.Str()


class GetCommentsResponseSchema(Schema):
    id = fields.Int()
    user_name = fields.Str()
    profile_url = fields.Str()
    profile_mimetype = fields.Str()
    content = fields.Str()
    date_posted = fields.Str()


class ListCommentsResponseSchema(Schema):
    comments = fields.List(fields.Nested(GetCommentsResponseSchema))
