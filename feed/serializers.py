from rest_framework import serializers

from common.serializers import BaseModelSerializer
from feed.models import Source, Post
from user.serializers import ProfileSerializer


class SourceSerializer(BaseModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Source
        exclude = ['updated_at']


class CurrentSourceDefault(object):
    def set_context(self, serializer_field):
        self.source_id = serializer_field.context['source'].pk

    def __call__(self):
        return self.source_id

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class PostSerializer(BaseModelSerializer):
    source = SourceSerializer(read_only=True)
    source_id = serializers.HiddenField(
        write_only=True,
        default=CurrentSourceDefault()
    )
    created = serializers.DateTimeField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Post
        exclude = ['updated_at']

    def validate(self, attrs):
        source = self.context.get('source')
        if not Source.get_by_pk(source.pk):
            raise serializers.ValidationError({
                'source': {
                    'source_id': 'The requested source is not found'
                }
            })
        return attrs
