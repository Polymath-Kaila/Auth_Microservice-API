from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from django.contrib.auth import authenticate
from datetime import datetime,timezone
from django.conf import settings
import json 
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from accounts.utils import (
    generate_otp, set_otp, get_otp,
    can_resend, increment_attempts, get_attempts,
    revoke_otp, OTP_MAX_ATTEMPTS, OTP_TTL_SECONDS
)

from accounts.tasks import send_otp_email

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
        
        


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")

        try:
            # Validate + decode refresh token
            refresh = RefreshToken(refresh_token)

        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        
        # extract jti and user_id and exp
        jti = refresh.get("jti")
        user_id = refresh["user_id"]
        exp = refresh.get("exp")
        
        # check redis blacklist
        redis_client = settings.REDIS_CLIENT
        redis = f"token:{jti}"
        if redis_client.exists(key):
            raise serializers.ValidationError("Refresh token has been revoked (logged out)")
        
        

        attrs["user_id"] = user_id
        attrs["refresh"] = refresh
        attrs["jti"] = jti
        attrs["exp"] = exp
        

        return attrs

    def create(self, validated_data):
        refresh = validated_data["refresh"]

        # Generate a new access token
        new_access = refresh.access_token

        return {
            "access": str(new_access),
            "refresh": str(refresh),
        }
        
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    
    def validate(self,attrs):
        refresh_token = attrs.get("refresh")
        
        try:
        
            refresh = RefreshToken(refresh_token)
            
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token")
        
        #extract jti,user_id,exp
        jti = refresh.get("jti")
        user_id = refresh.get("user_id")
        exp = refresh.get("exp")
        
        if not jti:
            raise serializers.ValidationError("Token missing unique id (jti)")
        
        attrs["refresh"] = refresh
        attrs["jti"] = jti
        attrs["user_id"] = user_id
        attrs["exp"] = exp
        
        
    def create(self,validated_data):
        """ 
        Blacklist the refresh token by storing metadata in Redis with TTL = (exp - now)
        """
        redis_client = settings.REDIS_CLIENT
        jti = validated_data["jti"]
        user_id = validated_data["user_id"]
        exp = validated_data["exp"]
        
        #complete TTL in seconds
        
        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        ttl = exp - now_ts
        if ttl <= 0:
            
            #token already expired - nothing to store
            return{"detail": "Token already expired."}
        
        key = f"token:{jti}"
        
        value = {
            "user_id":user_id,
            "revoked_at":now_ts,
            "exp":exp,
            "type":"refresh"       
        }
        
        redis_client.set(key, json.dumps(value),ex=ttl)
        
        return{"detail":"logged out (refresh token revoked)."}
        
        
# accounts/serializers.py
User = get_user_model()


# -------------------- SEND OTP --------------------
class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"].lower()

        # Ensure user actually exists for email verification
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("No account is registered with this email.")

        if not can_resend(email):
            raise serializers.ValidationError("OTP already sent. Try again soon.")

        attrs["email"] = email
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]

        # Generate OTP
        otp = generate_otp()

        # Store OTP in Redis with TTL
        set_otp(email, otp)

        # Send OTP async
        send_otp_email.delay(email, otp)

        return {"detail": "OTP sent successfully."}


# -------------------- VERIFY OTP --------------------
class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)

    def validate(self, attrs):
        email = attrs["email"].lower()
        otp = attrs["otp"].strip()

        stored = get_otp(email)

        if not stored:
            raise serializers.ValidationError("OTP expired or not found. Request a new code.")

        attempts = get_attempts(email)
        if attempts >= OTP_MAX_ATTEMPTS:
            revoke_otp(email)
            raise serializers.ValidationError("Too many failed attempts. OTP invalidated.")

        attrs["email"] = email
        attrs["otp"] = otp
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        otp = validated_data["otp"]

        stored = get_otp(email)

        if stored != otp:
            attempts = increment_attempts(email)
            remaining = OTP_MAX_ATTEMPTS - attempts
            raise serializers.ValidationError(f"Invalid OTP. {remaining} attempts left.")

        # OTP correct → verify user
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        # Clean Redis keys
        revoke_otp(email)

        return {"detail": "Email verified successfully!"}

