from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

"""
serializers comes from djongorestframework module
we convert User to JSON and validate input
here think which field should API expose when returning user info?
  1.email {identifies a user,required for login,safe to expose}
  2.is_verified {allows frontend to know whether to show: verify your email, help ui}
  
"""
          
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length = 6
        )
    """ 
    password will only be accepted in req but never returned in res
    we control password validation
    we prevent showing hash or raw password
    
    """
    
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name","password"]
        
    def create(self,validated_data):
            """
            create is the first lifecycle django method
            validated_data DRF serializer method for clean, safe data
            extract password before creating user
            this prevents password from being saved as plain text
            """ 
            password = validated_data.pop('password')
            
            """ 
            create user using UserManager
            create_user in UserManager handles hashing + normalization
            """
            user = User.objects.create_user(
                password = password,
                **validated_data
            )
            
            """ 
            generate JWT tokens
            simpleJWT creates tokens for new users
            gives as refresh.access_token & refresh
            """ 
            
            refresh = RefreshToken.for_user(user)
            
            """ 
            return dictionary gives the fronted everything it needs
            """
            return{
                "email": user.email,
                "is_verified": user.is_verified,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }