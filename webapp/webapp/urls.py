"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from webapp.views import Register, Profile, Index, TableJoin, TableUnJoin, BJTable, RoundStart

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view()),
    path('signup/', Register.as_view()),
    path('', Index.as_view(), name="index"),
    path('table/<table_id>/join/', TableJoin.as_view(), name="join_table"),
    path('table/<table_id>/unjoin/', TableUnJoin.as_view(), name="unjoin_table"),
    path('table/<table_id>/start-play/', RoundStart.as_view(), name="start_round"),
    path('table/<table_id>/', BJTable.as_view()),
    path('profile/', Profile.as_view()),
    path('admin/', admin.site.urls),
]
