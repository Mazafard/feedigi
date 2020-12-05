import re

from rest_framework import serializers


class CheckNotExistValidator(object):
    def __init__(self, query_set, field='id', message=None):
        self.query_set = query_set
        self.field = field
        self.message = message if message else \
            'The requested {field_name}({value}) is exists.'

    def __call__(self, value):
        if self.query_set.filter(**{self.field: value}).exists():
            message = self.message.format(field_name=self.field, value=value)
            raise serializers.ValidationError(message)


class CheckExistValidator(object):
    def __init__(self, query_set, field='id', message=None):
        self.query_set = query_set
        self.field = field
        self.message = message if message else \
            'The requested {field_name}({value}) is not exists.'

    def __call__(self, value):
        if not self.query_set.filter(**{self.field: value}).exists():
            message = self.message.format(field_name=self.field, value=value)
            raise serializers.ValidationError(message)


class CheckMobileNumber(object):
    def __call__(self, value):
        if not re.match("09[\d]{9}", value):
            message = _('The requested cellphone ({cellphone}) is not valid.').format(
                cellphone=value)
            raise serializers.ValidationError(message)
