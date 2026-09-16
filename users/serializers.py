from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.models import Group

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    GROUP_CHOICES = [
        ('Landlord', 'Арендодатель'),
        ('Tenant', 'Арендатор'),
    ]

    group = serializers.ChoiceField(choices=GROUP_CHOICES, write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'group')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        group_name = validated_data.pop('group')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')