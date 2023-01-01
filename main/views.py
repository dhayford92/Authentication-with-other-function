from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, logout
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .models import User
from .serializers import LoginSerializer



class GoogleLogin(GenericAPIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        
        credentials = Credentials.from_authorized_user_info(info=request, access_token=access_token)
        service = build('people', 'v1', credentials=credentials)
        
        # Call the People API to retrieve the user's profile
        profile = service.people().get(resourceName='people/me').execute()
        
        # Extract the user's email and name from the profile
        email = profile.get('emailAddresses')[0].get('value')
        name = profile.get('names')[0].get('displayName')
        
        # Use the email to authenticate or create a new user in your Django app
        user, created = User.objects.get_or_create(email=email)
        user_password = 'aWfj1419fmfwln-@sucnlsjhsajisj4fbv'
        
        if created:
            user.fullname = name
            user.provider = 'google'
            user.set_password(user_password)
            user.save()
            
        auth_user = authenticate(email=user.email, password=user_password)
        
        if auth_user != None:
            serializer = LoginSerializer(auth_user)
            return Response(serializer.data, status=200)
        else:
            return Response({'message': 'Invalid Credentails'}, status=status.HTTP_401_UNAUTHORIZED)


