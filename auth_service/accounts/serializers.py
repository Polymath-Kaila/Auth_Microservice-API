from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


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
            
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    
    def validate(self,attr):
        
        """ 
        this method is where we do:
         1. authentication
         2. existence checking
         3. password checking
         4. business rules, is_verified
         5.attach user to validated_data
         attr holds typed data email & password
        """
        
        email = attr.get("email")
        password = attr.get("password")
        
        """ 
          this pulls raw email and password data
        """
        
        
        user = authenticate(email = email, password = password)
        """ 
          this checks:
           Does user with this email exist?
           Does the password match
           is the user active
        """
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        """ 
         if authentication fails we raise a nice error
         
        """
        
        if not user.is_verified:
            raise serializers.ValidationError("Please verify your email first")
        """ 
         optional we block unverified users from being authenticated
        """
        
        attr["user"] = user
        return attr
    """ 
     attach the authenticated user so create() method can access it 
    """
    
    def create(self,validated_data):
        """ 
        for tokens
        """
        user = validated_data["user"]
        
        refresh = RefreshToken.for_user(user)
        
        return{
            "email":user.email,
            "is_verified":user.is_verified,
            "access":str(refresh.access_token),
            "refresh":str(refresh)
        }

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        field = ["email", "is_verified"]
        
        
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")

        try:
            # Validate + decode refresh token
            refresh = RefreshToken(refresh_token)

            # Get the user from token
            user_id = refresh["user_id"]

        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")

        attrs["user_id"] = user_id
        attrs["refresh"] = refresh

        return attrs

    def create(self, validated_data):
        refresh = validated_data["refresh"]
        user_id = validated_data["user_id"]

        # Generate a new access token
        new_access = refresh.access_token

        return {
            "access": str(new_access),
            "refresh": str(refresh),
        }
