"""
URL configuration for Note_taking_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from authentication.views import home,terms_of_service,privacy_policy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='home'),
    path('terms_of_service/',terms_of_service,name='terms_of_service'),
    path('privacy_policy/',privacy_policy,name='privacy_policy'),
    path('application/',include('application.urls')),
    path('auth/',include('authentication.urls')),
]   
