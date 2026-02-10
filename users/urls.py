from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns=[
    path('register/user', views.create_user),
    path('register/admin', views.create_admin),
    path('get', views.get_users),
    path('<int:id>', views.get_user),
    path('update', views.update_user),
    path('delete/<int:id>', views.delete_user),
    path('token', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh')
]