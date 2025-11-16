from django.db import IntegrityError, transaction

""" 
 we need transaction.atomic() to make create + token gen atomic ie if something fails db rolback
 integrity error catches unique constraints ie duplicate email
"""
from rest_framework import status           # for status codes
from rest_framework.response import Response # for responses
from rest_framework.views import APIView      
from rest_framework.permissions import AllowAny 

from .serializers import SignupSerializer

class SignupView(APIView):
    """
    this endpoint supports manual http methods(post, etc)
    since we want to design exactly what happens on POST(signup)
    
    """

    permission_classes = [AllowAny]
    """ 
    signup must be public
    if we used `IsAuthenticated`, only looged-in users could sign up (makes no sense)
    """

    def post(self, request, *args, **kwargs):
        """ 
        its a lifecycle drf view method 
        request is an object that includes : request.data, .user etc
        this function is executed everytime a POST request arrives
        inside:
            1. we read request data
            2. we validate via serializer
            3. save and return response
            
        """
      
        serializer = SignupSerializer(data=request.data)
        """ 
        this takes the JSON from req body and feed into the serializer
        """
        
        serializer.is_valid(raise_exception=True)
        """ 
        this runs validation rules
        checks required fields 
        if invalid automatically returns HTTP 400 with error details
        we dont need to write manual checks
        """

        try:
            with transaction.atomic():
                """ 
                this ensures either the entire signup succeed OR nothing is saved to db
                if something fails:
                  * user ins't created
                  * db is not corrupted
                  * tokens are not generated for non exustent users
                Atomicity = proffessional approach
                """
               
                result = serializer.save()
                """ 
                this line :
                - calls SignupSerializer.create()
                - which calls our UserManager
                - which craetes the user
                - which hashes the password
                - which normalizes the email
                - which sets flags ie is_staff
                - which saves the user
                - which generates JWT tokens
                - then retursn the res dict
                
                """
        except IntegrityError as exc:
            
            return Response(
                {"detail": "User with that email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        
        return Response(result, status=status.HTTP_201_CREATED)
            # sends JSON back to frontend with a 201 created
