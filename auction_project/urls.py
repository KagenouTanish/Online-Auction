from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from auction_project.admin import AuctionHubAdminSite

admin_site = AuctionHubAdminSite(name='auctionhub_admin')

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('auctions.urls')),
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
