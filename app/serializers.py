from .models import Custom_User, Event

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class Custom_User_Serializer(ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(read_only=True)
    # name = serializers.IntegerField()
    class Meta:
        model = Custom_User
        fields = ['id', 'name', 'phone_number', 'country', 'avatar']


class EventSerializer(ModelSerializer):
    owner = Custom_User_Serializer()
    user_liked = Custom_User_Serializer(many=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'owner', 'data', 'time',
                  'location', 'image', 'user_liked']
