from rest_framework import serializers
from .models import User



class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=200)
    
    class Meta:
        model = User 
        fields = ['fullname', 'email', 'password', 'phone', 'tokens']
        read_only_fields = ['fullname', 'phone', 'tokens']
        

 