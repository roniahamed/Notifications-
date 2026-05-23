import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()
token_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc5NTQ5NDI5LCJpYXQiOjE3Nzk1NDU4MjksImp0aSI6ImM2YzYwZjEwYTNkMTRkYmJiMDVlYTZiNDg1MmJkY2JlIiwidXNlcl9pZCI6MX0.kpDHH_bENkhhBqnGD29HHqZXeyKFbi_le1HUM8-ef80"

try:
    token = AccessToken(token_key)
    print("Token is valid. User ID:", token["user_id"])
    user = User.objects.get(id=token["user_id"])
    print("User found:", user)
except Exception as e:
    import traceback

    traceback.print_exc()
