# Python
import uuid

# Django
from django.contrib.auth.models import Permission, Group

# Models
from .models import User, Profile

# Django RestFramework
from rest_framework import serializers



class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id','name']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'




class UserRegistrationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    fullname = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    passwordconf = serializers.CharField(write_only=True)
    rol = serializers.ChoiceField(
        choices=['0', '1', '2', '3']
        )

    def validate(self, data):
        if not data.get('password') or not data.get('passwordconf'):
            raise serializers.ValidationError("Ingresa una contraseña y confirmala.")

        if data.get('password') != data.get('passwordconf'):
            raise serializers.ValidationError("Las contraseñas no coinciden.")

        data['username'] = uuid.uuid4().hex[:30]
        data.pop('passwordconf')
        return data

    def  create(self, validated_data):
        user= User.objects.create_user(**validated_data)
        return user
