from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from ..serializers import UserSerializer


class TokenRegisterView(APIView): 
    def post(self, request, *args, **kwargs): 
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid(): 
            return Response(status=400) 
        new_user = serializer.save() 
        return Response({
            'token': str(Token.objects.get(user=new_user))
        }, status=200)


