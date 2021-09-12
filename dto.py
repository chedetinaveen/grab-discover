from marshmallow import Schema, fields


class CreateMerchantSchema(Schema):
    name = fields.Str()
    logo = fields.Str()


class GetMerchantResponseSchema(Schema):
    name = fields.Str()
    logo = fields.Str()


class UpdateMerchantSchema(Schema):
    name = fields.Str()
    logo = fields.Str()
