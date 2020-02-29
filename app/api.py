from rest_framework.routers import DefaultRouter

from django.urls import path, include
from django.conf.urls import url



urlpatterns = [
    url('user/',
        include(('accounts.urls','users'))
    ),    
    url('poll/',
        include(('polls.urls','polls'))
    )
]
