from rest_framework import exceptions, serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from rest_framework_expiring_authtoken.models import ExpiringToken
from django.contrib.auth import authenticate

from .models import TongueUser
from .decorators import app_view


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    uuid = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        uuid = attrs.get('uuid')

        if email and uuid:
            user = authenticate(email=email, uuid=uuid)

            if user:
                if not user.is_active:
                    msg = 'Invalid user credentials.'
                    raise exceptions.ValidationError(msg)
            else:
                try:
                    user = TongueUser(email=email, phone_uuid=uuid, username=email)
                    user.save()
                except:
                    msg = 'Invalid user credentials.'
                    raise exceptions.ValidationError(msg)

                user = authenticate(email=email, uuid=uuid)

                if not user:
                    msg = 'Invalid user credentials.'
                    raise exceptions.ValidationError(msg)

        else:
            msg = 'Invalid user credentials.'
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs

class ObtainExpiringAuthToken(ObtainAuthToken):

    model = ExpiringToken

    def post(self, request):
        """Respond to POSTed credentials with token."""
        serializer = AuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            token, _ = ExpiringToken.objects.get_or_create(
                user=serializer.validated_data['user']
            )

            if token.expired():
                # If the token is expired, generate a new one.
                token.delete()
                token = ExpiringToken.objects.create(
                    user=serializer.validated_data['user']
                )

            data = {'token': token.key}
            return Response(data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

obtain_token = app_view(ObtainExpiringAuthToken.as_view())
