from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .serializers import SignupSerializer

class SignupView(APIView):
    """
    POST /api/accounts/signup/
    Body: { "email": "...", "password": "...", "first_name": "...", "last_name": "..." }
    Returns: 201 + { email, is_verified, access, refresh } on success.
    """

    permission_classes = [AllowAny]  # public endpoint

    def post(self, request, *args, **kwargs):
        # 1) Validate input with serializer (raises 400 with details if invalid)
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2) Use a DB transaction to ensure atomicity: either user created + tokens generated or nothing
        try:
            with transaction.atomic():
                # Our serializer.create() returns a dict with tokens + user fields (per your serializer)
                result = serializer.save()
        except IntegrityError as exc:
            # Handle unique constraint errors (e.g. duplicate email) gracefully
            return Response(
                {"detail": "User with that email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3) Return the created payload (already a dict with tokens + email + is_verified)
        return Response(result, status=status.HTTP_201_CREATED)
