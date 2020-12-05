import base64

from django import forms
from django.core.files.base import ContentFile
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html
from rest_framework import serializers


class ImageField(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        if "readonly" in self.attrs and self.attrs['readonly']:
            return "<img src=\"{url}\" height=250/>".format(url=self.attrs['url'])

        if isinstance(attrs, dict):
            attrs['name'] = name
        else:
            attrs = {
                'name': name
            }
        final_attrs = self.build_attrs(attrs)
        input_ = """<input type="file" {}>{}</input>"""
        if 'url' in self.attrs and self.attrs['url']:
            input_ = "<img src=\"{url}\" height=250 />{input}".format(
                url=self.attrs['url'], input=input_)

        return format_html(input_, flatatt(final_attrs), force_text(value))


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super(Base64ImageField, self).to_internal_value(data)
