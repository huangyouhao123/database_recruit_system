"""
URL configuration for djangoProject2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from index import views

urlpatterns = [
    path('', views.login),
    path('ur/', views.ur),
    path('ur/<int:userid>/', views.ur_show),
    path('ue/', views.ue),
    path('ue/<int:userid>/', views.ue_show),
    path('ua/', views.ua),
    path('uh/', views.uh),
    path('uh/<int:userid>/', views.uh_show),
    path('jobs/', views.job_list),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('choose/', views.choose),
    path('interview/result/',views.interviewResult),
    path('user/register/',views.register),
    path('interview/',views.interview),
    path('createjob/',views.createjob),
    path('audit/',views.audit),
    path('result/',views.result),
    path('history/',views.history)
]
