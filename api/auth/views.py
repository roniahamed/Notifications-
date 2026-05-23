import uuid
import logging
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UpdateFCMTokenSerializer,
)
from .services import (
    verify_otp,
    store_reset_token,
    verify_reset_token,
    send_password_reset_email,
)
from .tasks import send_verification_email_task
from .throttles import OTPThrottle, LoginThrottle

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email_task.delay(user.email)
        return Response(
            {"detail": "Registration successful. Please verify your email with the OTP sent."},
            status=status.HTTP_201_CREATED,
        )


class ResendOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]
    
    from drf_spectacular.utils import extend_schema, inline_serializer
    from rest_framework import serializers
    serializer_class = serializers.Serializer
    
    @extend_schema(request=inline_serializer("ResendOTP", {"email": serializers.EmailField()}))

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email=email).exists():
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        send_verification_email_task.delay(email)
        return Response({"detail": "OTP resent."}, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        if not verify_otp(email, otp):
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.is_verified = True
            user.save(update_fields=["is_verified"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]
    serializer_class = LoginSerializer


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    from drf_spectacular.utils import extend_schema, inline_serializer
    from rest_framework import serializers
    serializer_class = serializers.Serializer
    
    @extend_schema(request=inline_serializer("Logout", {"refresh": serializers.CharField()}))

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class ForgotPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If that email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

        token = str(uuid.uuid4())
        store_reset_token(email, token)
        send_password_reset_email(email, token)
        return Response({"detail": "If that email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        email = verify_reset_token(token)
        if not email:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save(update_fields=["password"])
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)


class UpdateFCMTokenView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateFCMTokenSerializer

    def patch(self, request):
        serializer = UpdateFCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.fcm_token = serializer.validated_data["fcm_token"]
        request.user.save(update_fields=["fcm_token"])
        return Response({"detail": "FCM token updated."}, status=status.HTTP_200_OK)
