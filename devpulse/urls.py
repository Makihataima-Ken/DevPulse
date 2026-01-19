"""
URL configuration for devpulse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
# devpulse/urls.py
from django.contrib import admin
from django.urls import path
from activities.views import (
    LoginView,
    SignupView,
    ActivityView,
    StreakView,
    TestAuthView,
    GitHubActivityView,
    GitHubStatsView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/signup/', SignupView.as_view(), name='signup'),
    path('test-auth/', TestAuthView.as_view()),

    # Core features
    path('api/activities/', ActivityView.as_view()),
    path('api/streak/', StreakView.as_view()),

    # GitHub
    path('api/github/sync/', GitHubActivityView.as_view()),
    path('api/github/stats/', GitHubStatsView.as_view()),
]
