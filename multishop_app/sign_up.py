from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.parsers import JSONParser
from .models import *

class ApiUserRegister(APIView):

    def post(self, request):

        response = {} 
        try:
            data = JSONParser().parse(request)
            if data.get('email') is None:
                response['message'] = 'key email not found'
                raise Exception('key username not found')

            if data.get('password') is None:
                response['message'] = 'key password not found'
                raise Exception('key password not found')
            check_user = CustomUser.objects.filter(email=data.get('email')).first()
            if check_user:
                response['message'] = 'email already taken'
                raise Exception('email already taken')

            user_obj = CustomUser.objects.create(email=data.get('email'))
            user_obj.set_password(str(data.get('password')))
            user_obj.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user_obj)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response['message'] = 'User Created Successfully'
            response['status'] = 200
            response['access_token'] = access_token
            response['refresh_token'] = refresh_token
        except Exception as e:
            print(e)

        return Response(response)
    