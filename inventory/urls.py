"""ocean URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from . import views

urlpatterns = [
    path('/', views.inventory, name='inventory'),
    path('assets/', views.assets, name='assets'),
    path('assets/newgroup/',views.newgroup,name='newgroup'),
    path('assets/save-new',views.assets_new,name='assets_new'),
    path('purchasing/', views.purchasing, name='purchasing'),
    path('purchasing/new/', views.new_purchasing_order, name='new_purchasing_order'),
    path('grn/', views.grn, name='grn'),
    path('grn/new/', views.new_grn, name='new-grn'),

]

# handler404 = 'blog.views.handler404'
