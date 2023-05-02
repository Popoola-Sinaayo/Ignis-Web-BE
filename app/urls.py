from django.urls import path
from .views import Login_User, Register_User, All_Event_View, User_Event_View

urlpatterns = [
    path("register", Register_User.as_view()),
    path("login", Login_User.as_view()),
    path("all-events", All_Event_View.as_view()),
    path("user/event", User_Event_View.as_view())
]
