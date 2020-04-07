from cic_network.cicn_users import views

from rest_framework.routers import DefaultRouter
from django.urls import path

api = DefaultRouter()

api.register(r'user', views.UserViewSet)
api.register(r'sn', views.SocialNetworkViewSet)

urlpatterns = api.urls + [
    path("auth", views.AuthView.as_view(), name="auth"),
]
