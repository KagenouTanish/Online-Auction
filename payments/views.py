from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import uuid
from .models import Payment, Transaction
from .forms import PaymentForm
from auctions.models import Auction


@login_required
def process_payment(request, auction_slug):
    auction = get_object_or_404(Auction, slug=auction_slug)
    if auction.is_active:
        messages.error(request, 'Auction is still active.')
        return redirect('auction_detail', slug=auction.slug)
    highest_bid = auction.bids.first()
    if not highest_bid or highest_bid.bidder != request.user:
        messages.error(request, 'You are not the winner of this auction.')
        return redirect('auction_detail', slug=auction.slug)
    if Payment.objects.filter(auction=auction, buyer=request.user, status='COMPLETED').exists():
        messages.error(request, 'Payment already completed for this auction.')
        return redirect('payment_detail', auction_slug=auction.slug)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = Payment.objects.create(
                auction=auction,
                buyer=request.user,
                seller=auction.seller,
                amount=auction.current_price,
                payment_method=form.cleaned_data['payment_method'],
                status='COMPLETED',
                transaction_id=str(uuid.uuid4()).replace('-', '')[:16],
            )
            Transaction.objects.create(
                payment=payment,
                type='payment',
                amount=payment.amount,
                description=f'Payment for {auction.title}',
            )
            messages.success(request, 'Payment processed successfully.')
            return redirect('payment_detail', auction_slug=auction.slug)
    else:
        form = PaymentForm()
    return render(request, 'payments/process_payment.html', {
        'form': form,
        'auction': auction,
        'amount': auction.current_price,
    })


@login_required
def payment_history(request):
    payments = Payment.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).order_by('-created_at')
    return render(request, 'payments/payment_history.html', {'payments': payments})


@login_required
def payment_detail(request, auction_slug):
    payment = get_object_or_404(Payment, auction__slug=auction_slug, buyer=request.user)
    transactions = payment.transactions.all()
    return render(request, 'payments/payment_detail.html', {
        'payment': payment,
        'transactions': transactions,
    })
