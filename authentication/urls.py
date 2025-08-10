from django.urls import path
from . import views
urlpatterns=[
path('login/',views.Login_views,name='login_page'),
path('signup/',views.SignUp_views,name='signup_page'),
path('logout/',views.Logout_views,name='logout_page'),
]