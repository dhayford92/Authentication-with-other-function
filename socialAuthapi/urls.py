from django.contrib import admin
from django.urls import path
from main.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/googlelogin/', GoogleLogin.as_view()),
    path('api/emaillogin/', EmailLogin.as_view()),
    path('api/otp/', OptVerify.as_view()),
]
