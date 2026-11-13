from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Address
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)
    class Meta: model = User; fields = ["id", "email", "username", "first_name", "last_name", "password"]
    def create(self, validated_data): return User.objects.create_user(**validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta: model = User; fields = ["id", "email", "username", "first_name", "last_name"]; read_only_fields = ["id", "email"]

class AddressSerializer(serializers.ModelSerializer):
    class Meta: model = Address; exclude = ["user"]
