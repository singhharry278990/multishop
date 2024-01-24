from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth import login
from rest_framework import status
from .serializer import *

class LoginView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            response_data = {
                "message": "Login successfully",
                "status": status.HTTP_200_OK
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)