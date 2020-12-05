from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from common import errors
from common.auth import CustomTokenAuthentication
from common.models import CustomUser
from common.response import ErrorResponse, Response
from common.views import BaseApiView
from user import serializers


class UserRegisterApiView(BaseApiView):
    def post(self, request):
        serializer = serializers.UserRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(errors.USER_DATA_INPUT_IS_NOT_VALID,
                                 errors=serializer.errors)

        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLoginApiView(BaseApiView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(errors.USER_DATA_INPUT_IS_NOT_VALID,
                                 errors=serializer.errors)

        data = {
            'token': serializer.instance.get_new_auth_token(),
            'profile': serializers.ProfileSerializer(serializer.instance).data
        }

        return Response(data=data)


class ProfileApiView(BaseApiView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = serializers.ProfileSerializer(request.user)
        # todo Sorry for following line :-(
        return Response(data={'profile': serializer.data})

    def put(self, request):
        serializer = serializers.ProfileSerializer(instance=request.user,
                                                   data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(errors.USER_DATA_INPUT_IS_NOT_VALID,
                                 errors=serializer.errors)

        serializer.save()

        return Response(data=serializer.data)


class ChangePasswordApiView(BaseApiView):
    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        serializer = serializers.ChangePasswordSerializer(instance=request.user,
                                                          data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(errors.USER_DATA_INPUT_IS_NOT_VALID,
                                 errors=serializer.errors)

        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetPasswordApiView(BaseApiView):
    def post(self, request):
        serializer = serializers.ResetPasswordInputSerializer(instance=request.user,
                                                              data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(errors.USER_DATA_INPUT_IS_NOT_VALID,
                                 errors=serializer.errors)

        user = CustomUser.get_with_email(serializer.validated_data['email'])

        user.send_password_verification_email()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailApiView(BaseApiView):
    def get(self, request, verification_text):
        user = CustomUser.get_with_email_verification(verification_text)

        if not user:
            return ErrorResponse(errors.THE_REQUESTED_DATA_IS_NOT_FOUND)

        user.verify_email()

        data = {
            'token': user.get_new_auth_token(),
            'profile': serializers.ProfileSerializer(user).data
        }

        return Response(data=data)


class VerifyPasswordApiView(BaseApiView):
    def get(self, request, verification_text):
        user = CustomUser.get_with_password_verification(verification_text)

        if not user:
            return ErrorResponse(errors.THE_REQUESTED_DATA_IS_NOT_FOUND)

        user.verify_email()

        data = {
            'token': user.get_new_auth_token(),
            'profile': serializers.ProfileSerializer(user).data
        }

        return Response(data=data)

