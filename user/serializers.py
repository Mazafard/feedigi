from rest_framework import serializers

from common import validators
from common.models import CustomUser
from common.serializers import BaseSerializer, BaseModelSerializer
from common.validators import CheckNotExistValidator, CheckMobileNumber
from django.utils.translation import gettext_lazy as _


class UserRegisterSerializer(BaseSerializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(validators=[CheckNotExistValidator(
        CustomUser.objects.all(), 'email'
    )])
    cellphone = serializers.CharField(validators=[CheckMobileNumber(), CheckNotExistValidator(
        CustomUser.objects.all(), 'cellphone'
    )])
    password = serializers.CharField(max_length=255, min_length=6)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        # @todo send user send_verification_email()
        return user


class UserLoginSerializer(BaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=255)

    def validate(self, attr):
        user = CustomUser.objects.filter(email=attr['email']).first()  # type: CustomUser
        if not user:
            raise serializers.ValidationError({
                'email': _('The requested email is not found')
            })

        if not user.is_email_verified:
            raise serializers.ValidationError({
                'email': _('The requested email is not verified')
            })

        if not user.check_password(attr['password']):
            raise serializers.ValidationError({
                'password': _('The requested password is not valid')
            })
        self.instance = user
        return attr


class ProfileSerializer(BaseModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'cellphone')


class ChangePasswordSerializer(BaseSerializer):
    def create(self, validated_data):
        pass

    password = serializers.CharField(min_length=6, max_length=255)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class ResetPasswordInputSerializer(BaseSerializer):
    email = serializers.CharField(
        validators=[validators.CheckExistValidator(CustomUser.objects, 'email')])
