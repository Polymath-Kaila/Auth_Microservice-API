from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from accounts.managers import UserManager

"""
Abstractbaseuser is found in the django.contrib.auth.base_user module.
PermissionsMixin is found in the django.contrib.auth.models module.
we use AbstractBaseUser other than traditional abstract user since we rewrite our own fields
"""

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True,)
    first_name = models.CharField(blank = True, max_length = 50)
    last_name = models.CharField(blank=True, max_length=50, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add =True)
    
    
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =[]
    
    objects = UserManager()
    
    


    