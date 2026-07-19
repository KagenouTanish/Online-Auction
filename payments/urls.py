from django.urls import path
from . import views

urlpatterns = [
    path('pay/<slug:auction_slug>/', views.process_payment, name='process_payment'),
    path('history/', views.payment_history, name='payment_history'),
    path('detail/<slug:auction_slug>/', views.payment_detail, name='payment_detail'),
]
