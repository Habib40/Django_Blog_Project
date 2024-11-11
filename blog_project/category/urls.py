# This is category urls page
from django.urls import path
from . import views

urlpatterns=[
    path('category/',views.cat,name='cat'),
]