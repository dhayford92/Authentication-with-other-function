from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from rest_framework_simplejwt.tokens import RefreshToken

import random
from datetime import timedelta
from django.utils import timezone


class UserManger(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **kwargs):
        if email is None:
            raise ValueError({"message": "Email account must be provided"})

        email = self.normalize_email(email)
        now = timezone.now()
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            last_login=now,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **kwargs):
        return self._create_user(email, password, False, False, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        user = self._create_user(email, password, True, True, **kwargs)
        user.save(using=self._db)
        return user
        
        


class User(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=230, null=True, blank=True)
    phone = models.CharField(max_length=230, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    provider = models.CharField(max_length=230, default='email', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff =  models.BooleanField(default=False)
    is_superuser =  models.BooleanField(default=False)
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now=True)
    objects = UserManger()
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    def get_email(self):
        return self.email
    
    @property
    def tokens(self):
        token = RefreshToken.for_user(self)
        return {
            'refresh': str(token),
            'access': str(token.access_token)
        }
    
    class Meta:
        db_table = 'users'
        


class OtpCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, blank=True)
    expiration_time = models.DateTimeField(auto_now_add=False)
    
    def save(self, *args, **kwargs):
        
        number_list = [i for i in range(10)]
        code_items = []
        for i in range(4):
            num = random.choice(number_list)
            code_items.append(num)
        code_string = "".join(str(item) for item in code_items)
        self.code = code_string
        expiration_time = timezone.now() + timedelta(minutes=1, seconds=35)
        self.expiration_time = expiration_time
        super().save(*args, **kwargs)
        

