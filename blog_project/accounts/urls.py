from django.urls import path
from .import views



urlpatterns=[
    path('Registration/',views.RegisterView.as_view(),name='register'),
    path('accounts/login/',views.login_view,name='login'),
    path('account/activate/<uidb64>/<token>/',views.Activate,name='activate'),
]






