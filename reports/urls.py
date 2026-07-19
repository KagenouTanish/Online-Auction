from django.urls import path
from . import views

urlpatterns = [
    path('auctions/', views.auction_reports, name='auction_reports'),
    path('users/', views.user_reports, name='user_reports'),
    path('seller/', views.seller_reports, name='seller_reports'),
    path('my-bids/', views.my_bid_reports, name='my_bid_reports'),
]
