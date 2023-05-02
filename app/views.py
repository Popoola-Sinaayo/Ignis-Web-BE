from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .serializers import Custom_User_Serializer, EventSerializer
from .models import Event
import random
from django.utils import timezone
# Create your views here.

User = get_user_model()


class Register_User(APIView):
    permission_classes = [AllowAny, ]
    
    # function that generates access token for user
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
        }
    
    # handles get request
    def get(self, request):
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
    
    # creates new user
    def post(self, request):
        print(request.user.is_authenticated)
        try:
            email = request.data["email"]
            password = request.data["password"]
            name = request.data["name"]
        except KeyError:
            pass
        print(email, password)
        if email and password:
            user = User.objects.create_user(
                email=email, password=password, name=name)
            user.save()
            token = self.get_tokens_for_user(user)
            print("save")
            return Response({"status": "success", "message": "Data SuccessFully Created", "token": token}, status=status.HTTP_200_OK)
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
    
    # updates user saved information
    def put(self, request):
        print(request.user.is_authenticated)
        if request.user.is_authenticated:
            user = User.objects.get(email=request.user)
            print(user.country, user.phone_number)
            print(request.data.items())
            try:
                if request.FILES["avatar"]:
                    user.avatar = request.FILES["avatar"]
                    user.save()
            except MultiValueDictKeyError:
                pass
            try:
                for (key, data) in request.data.items():
                    print(key, data)
                    if key == 'password':
                        user.set_password(data)
                        user.save()
                    if key == 'country':
                        user.country = data
                        user.save()
                    if key == 'phone_number':
                        user.phone_number = data
                        user.save()
            except ValueError:
                return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
            user.refresh_from_db()
            return Response({"status": "success", "data": Custom_User_Serializer(user).data}, status=status.HTTP_200_OK)
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


class Login_User(APIView):
    permission_classes = [AllowAny, ]
    
    # function that generates access token for user
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
        }
        
    # request can be used to verify and fetch user information
    def get(self, request):
        print(request.user.is_authenticated)
        if request.user.is_authenticated:
            print(request.user)
            user = User.objects.get(email=request.user)
            user_serializer = Custom_User_Serializer(user).data
            return Response({"status": "success", "data": user_serializer})
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
    
    # contains the login in logic used
    def post(self, request):
        print(request.user.is_authenticated)
        print(request.data)
        try:
            email = request.data["email"]
            password = request.data["password"]
        except KeyError:
            pass
        print(email, password)
        if email and password:
            user = User.objects.filter(email=email)
            if user.exists():
                user = user[0]
                if check_password(password, user.password):
                    token = self.get_tokens_for_user(user)
                    print("save")
                    user_serializer = Custom_User_Serializer(user).data
                    return Response({"status": "success", "data": user_serializer, "token": token}, status=status.HTTP_200_OK)
                return Response({"status": "error", "message": "Login Error"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "error", "message": "Login Error"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "error", "message": "Login Error"}, status=status.HTTP_400_BAD_REQUEST)


class All_Event_View(APIView):
    permission_classes = [AllowAny,]

    # gets all event for all types of users
    def get(self, request):
        events = Event.objects.all()
        event_serializer = EventSerializer(events, many=True).data
        return Response(data={"message": "success", "data": event_serializer}, status=status.HTTP_200_OK)


class User_Event_View(APIView):
    permission_classes = [IsAuthenticated,]

    # gets new event for a particular authenticated user
    def get(self, request):
        user = User.objects.filter(email=request.user)
        print(user)
        if user.exists():
            event = Event.objects.filter(owner=user[0])
            print(event)
            event_serializer = EventSerializer(event, many=True).data
            return Response({"message": "success", "data": event_serializer}, status=status.HTTP_200_OK)
        return Response({"message": "error", "data": "No user found"}, status=status.HTTP_400_BAD_REQUEST)

    # creates new event for user
    def post(self, request):
        user = User.objects.filter(email=request.user)
        print(request.data)
        if user.exists():
            try:
                image = request.FILES["image"]
            except MultiValueDictKeyError:
                pass
            name = request.data["name"]
            data = request.data["data"]
            location = request.data["location"]
            if request.data["name"] and request.data["data"] and request.data["location"] and request.data["date"]:
                time = timezone.datetime.strptime(
                    request.data["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
                event = Event.objects.create(
                    owner=user[0], name=name, data=data, location=location, time=time, image=image)
                event.save()
                event_serializer = EventSerializer(event).data
                return Response({"message": "success", "data": event_serializer}, status=status.HTTP_200_OK)
            return Response({"message": "error", "data": "Please pass in required data"}, status=status.HTTP_200_OK)
        return Response({"message": "error", "data": "No user found"}, status=status.HTTP_400_BAD_REQUEST)

    # toggle likes request
    def put(self, request):
        user = User.objects.filter(email=request.user)
        if user.exists():
            event_id = request.data["event_id"]
            event = Event.objects.filter(id=event_id)
            if event.exists():
                user = user[0]
                event = event[0]
                # if event.owner == user:
                #     # if event owner toggles the like variable
                #     event.is_liked = not event.is_liked
                #     event.save()
                # else:
                print(event.user_liked.all())
                print(user)
                if user in event.user_liked.all():
                    event.user_liked.remove(user)
                    event.save()
                else:
                    event.user_liked.add(user)
                    event.save()
                all_events = Event.objects.all()
                event_serializer = EventSerializer(all_events, many=True).data
                return Response({"message": "success", "data": event_serializer}, status=status.HTTP_200_OK)
        return Response({"message": "error", "data": "No user found"}, status=status.HTTP_400_BAD_REQUEST)
