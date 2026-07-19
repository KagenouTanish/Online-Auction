from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Auction, Bid, Category
from .forms import AuctionForm, BidForm, CategoryForm


def home(request):
    featured = Auction.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:7]
    recent = Auction.objects.filter(is_active=True).order_by('-created_at')[:7]
    categories = Category.objects.all()
    return render(request, 'auctions/home.html', {
        'featured': featured,
        'recent': recent,
        'categories': categories,
    })


def auction_list(request):
    auctions = Auction.objects.filter(is_active=True)
    category_slug = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort', '-created_at')

    if category_slug:
        auctions = auctions.filter(category__slug=category_slug)
    if search:
        auctions = auctions.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    valid_sorts = {
        'price_asc': 'current_price',
        'price_desc': '-current_price',
        'newest': '-created_at',
        'ending_soon': 'end_time',
    }
    sort_field = valid_sorts.get(sort, '-created_at')
    auctions = auctions.order_by(sort_field)

    categories = Category.objects.all()
    chunk_size = 6
    auction_list = list(auctions)
    chunks = [auction_list[i:i+chunk_size] for i in range(0, len(auction_list), chunk_size)]
    return render(request, 'auctions/auction_list.html', {
        'auction_chunks': chunks,
        'total_count': len(auction_list),
        'categories': categories,
        'selected_category': category_slug,
        'search': search,
        'current_sort': sort,
    })


def auction_detail(request, slug):
    auction = get_object_or_404(Auction, slug=slug)
    bids = auction.bids.all().order_by('-amount')
    bid_form = BidForm()
    winner = None
    if not auction.is_active and auction.end_time < timezone.now():
        highest_bid = bids.first()
        if highest_bid:
            winner = highest_bid.bidder
    return render(request, 'auctions/auction_detail.html', {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
        'winner': winner,
    })


@login_required
def auction_create(request):
    if not request.user.profile.is_seller:
        messages.error(request, 'Only sellers can create auctions.')
        return redirect('home')
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.current_price = auction.starting_price
            auction.save()
            messages.success(request, 'Auction created successfully.')
            return redirect('auction_detail', slug=auction.slug)
    else:
        form = AuctionForm()
    return render(request, 'auctions/auction_form.html', {'form': form, 'title': 'Create Auction'})


@login_required
def auction_edit(request, slug):
    auction = get_object_or_404(Auction, slug=slug, seller=request.user)
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES, instance=auction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auction updated successfully.')
            return redirect('auction_detail', slug=auction.slug)
    else:
        form = AuctionForm(instance=auction)
    return render(request, 'auctions/auction_form.html', {'form': form, 'title': 'Edit Auction'})


@login_required
def auction_delete(request, slug):
    auction = get_object_or_404(Auction, slug=slug, seller=request.user)
    if request.method == 'POST':
        auction.delete()
        messages.success(request, 'Auction deleted successfully.')
        return redirect('my_auctions')
    return render(request, 'auctions/auction_confirm_delete.html', {'auction': auction})


@login_required
def bid_create(request, slug):
    auction = get_object_or_404(Auction, slug=slug, is_active=True)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount <= auction.current_price:
                messages.error(request, f'Bid must be greater than current price (${auction.current_price}).')
                return redirect('auction_detail', slug=auction.slug)
            bid = form.save(commit=False)
            bid.auction = auction
            bid.bidder = request.user
            bid.save()
            auction.current_price = amount
            auction.save()
            messages.success(request, 'Bid placed successfully.')
        else:
            messages.error(request, 'Invalid bid.')
    return redirect('auction_detail', slug=auction.slug)


@login_required
def my_auctions(request):
    auctions = Auction.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'auctions/my_auctions.html', {'auctions': auctions})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'auctions/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    auctions = Auction.objects.filter(category=category, is_active=True).order_by('-created_at')
    return render(request, 'auctions/category_detail.html', {
        'category': category,
        'auctions': auctions,
    })
