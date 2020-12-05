from rest_framework.serializers import Serializer, ModelSerializer


class BaseSerializer(Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class BaseModelSerializer(ModelSerializer):
    pass
