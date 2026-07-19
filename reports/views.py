from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from auctions.models import Auction, Bid
from payments.models import Payment


@staff_member_required
def auction_reports(request):
    total_auctions = Auction.objects.count()
    total_bids = Bid.objects.count()
    total_revenue = Payment.objects.filter(status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or 0
    active_auctions = Auction.objects.filter(is_active=True).count()
    ended_auctions = Auction.objects.filter(is_active=False).count()
    return render(request, 'reports/auction_reports.html', {
        'total_auctions': total_auctions,
        'total_bids': total_bids,
        'total_revenue': total_revenue,
        'active_auctions': active_auctions,
        'ended_auctions': ended_auctions,
    })


@staff_member_required
def user_reports(request):
    users = User.objects.annotate(
        total_auctions=Count('auctions', distinct=True),
        total_bids=Count('bids', distinct=True),
        total_payments=Count('payments_made', distinct=True),
    ).order_by('-date_joined')
    return render(request, 'reports/user_reports.html', {'users': users})


@login_required
def seller_reports(request):
    auctions = Auction.objects.filter(seller=request.user)
    total_auctions = auctions.count()
    total_bids = Bid.objects.filter(auction__seller=request.user).count()
    total_revenue = Payment.objects.filter(seller=request.user, status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or 0
    active_auctions = auctions.filter(is_active=True).count()
    return render(request, 'reports/seller_reports.html', {
        'total_auctions': total_auctions,
        'total_bids': total_bids,
        'total_revenue': total_revenue,
        'active_auctions': active_auctions,
        'auctions': auctions,
    })


@login_required
def my_bid_reports(request):
    bids = Bid.objects.filter(bidder=request.user).select_related('auction').order_by('-created_at')
    total_bids = bids.count()
    total_spent = bids.aggregate(total=Sum('amount'))['total'] or 0
    won_auctions = Auction.objects.filter(
        bids__bidder=request.user,
        is_active=False
    ).distinct().count()
    return render(request, 'reports/my_bid_reports.html', {
        'bids': bids,
        'total_bids': total_bids,
        'total_spent': total_spent,
        'won_auctions': won_auctions,
    })
