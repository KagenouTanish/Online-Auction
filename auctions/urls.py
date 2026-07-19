from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auctions/', views.auction_list, name='auction_list'),
    path('auction/create/', views.auction_create, name='auction_create'),
    path('auction/<slug:slug>/', views.auction_detail, name='auction_detail'),
    path('auction/<slug:slug>/edit/', views.auction_edit, name='auction_edit'),
    path('auction/<slug:slug>/delete/', views.auction_delete, name='auction_delete'),
    path('auction/<slug:slug>/bid/', views.bid_create, name='bid_create'),
    path('my-auctions/', views.my_auctions, name='my_auctions'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
]
