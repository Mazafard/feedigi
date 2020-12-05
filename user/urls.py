from django.urls import path

from user import views

urlpatterns = [
    path('register/',
         views.UserRegisterApiView.as_view(),name='register-user'),
    path('login/', views.UserLoginApiView.as_view(), name='login-user'),
    path('profile/', views.ProfileApiView.as_view()),
    path('reset-password/', views.ResetPasswordApiView.as_view()),
    path('change-password/', views.ChangePasswordApiView.as_view()),
    path('verify-email/<verification_text>', views.VerifyEmailApiView.as_view()),
    path('verify-password/<verification_text>', views.VerifyPasswordApiView.as_view()),
]
