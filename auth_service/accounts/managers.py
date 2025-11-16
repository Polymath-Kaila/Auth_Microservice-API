from django.contrib.auth.base_user import BaseUserManager
from django.db import models
""" 
BaseUserManager is a module found in django.contrib.auth.models
it is from it we inherit and expand our UserManager to handle:
   1.creating normal users
   2.creating superusers
   3.setting is_staff/is_super_user
   4.enforcing email login
   5.setting is_verified for superusers
"""

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    """ 
    create_user method must do 3 things:
     1.check if email provided
     2.normalize the email
     3.create user instance
     4.set password
     5.save
     6.return user
    """
    
    def create_superuser(self,email,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified',True)
        
        return self.create_user(email,password, **extra_fields)

    
    
    