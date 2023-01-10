from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, logout
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .models import OtpCode, User
from .serializers import LoginSerializer
from datetime import timedelta
from django.utils import timezone
import firebase_admin
from firebase_admin import credentials, messaging



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




class EmailLogin(GenericAPIView):
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if user != None:
            serializer = LoginSerializer(user)
            optcode, created = OtpCode.objects.get_or_create(user=user)
            expiration_time = timezone.now() + timedelta(minutes=1, seconds=30)
            optcode.expiration_time = expiration_time
            optcode.save()
            
            # url = "https://devp-sms03726-api.hubtel.com/v1/messages/send"

            # payload = json.dumps({
            #     "from": "233240209723",
            #     "to": f"233{optcode.user.phone}",
            #     "content": f"{optcode.code}"
            # })
            
            # headers = {
            #     'Authorization': 'Basic b21qdmN5ano6dG54a215ZWI=',
            #     'Content-Type': 'application/json'
            # }

            # response = requests.request("POST", url, headers=headers, data=payload)
            
            
            return Response(serializer.data, status=200)
        else:
            return Response({'message': 'Invalid Credentails'}, status=status.HTTP_401_UNAUTHORIZED)
        



class OptVerify(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        user = request.user
        code = request.data['code']
        
        optuser = OtpCode.objects.filter(user=user).first()
        
        if optuser:
            if optuser.code == str(code):
                if optuser.expiration_time < timezone.now():
                    return Response({'message': 'Code has expired'}, status=status.HTTP_400_BAD_REQUEST)
                else:    
                    return Response({'message': 'Account verified'}, status=200)
            else:
                return Response({'message': 'Wrong code'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User code not found'}, status=status.HTTP_204_NO_CONTENT)
            
            
            
#---sending notification through firebase
def send_notification(request):
    # Obtain the server key from your Firebase project settings
    server_key = 'AAAA8pkXGD8:APA91bFyH2v5XZP4lEPURdk7QcdH0KGhsZMLcsdj7k7eNLnhGa25saf8kI___25lqJRsyaGvSUUkky-Aj8QtXts0Ecg5GZTUEfFTyQgMEd1oOk0pO1VqoCC6bf62__hiAwPVeDgQu6I2'
    cred = credentials.Certificate(server_key)
    firebase_admin.initialize_app(cred)

    # Set up the notification payload and target device token``
    notification = messaging.Notification(title='My notification', body='Hello, world!')
    device_token = 'your_device_token'

    # Send the notification
    message = messaging.Message(notification=notification, token=device_token)
    messaging.send(message)