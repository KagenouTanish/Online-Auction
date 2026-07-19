from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from auctions.models import Auction, Bid
from payments.models import Payment


@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_auctions = Auction.objects.count()
    total_bids = Bid.objects.count()
    total_revenue = Payment.objects.filter(status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or 0
    active_auctions = Auction.objects.filter(is_active=True).count()
    recent_auctions = Auction.objects.order_by('-created_at')[:10]
    recent_payments = Payment.objects.filter(status='COMPLETED').order_by('-created_at')[:10]
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': total_users,
        'total_auctions': total_auctions,
        'total_bids': total_bids,
        'total_revenue': total_revenue,
        'active_auctions': active_auctions,
        'recent_auctions': recent_auctions,
        'recent_payments': recent_payments,
    })
