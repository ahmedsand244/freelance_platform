


from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('refund/', views.refund_view, name='refund'),
    path('game/', views.game_view, name='game'),
    path('pulse/', views.pulse_view, name='pulse'),
    path('legends/', views.legends_view, name='legends'),
    path('ref/<str:username>/', views.referral_redirect, name='referral'),
]
