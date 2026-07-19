from django.contrib import admin
from auction_project.admin import admin_site
from .models import Auction, Bid, Category


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'slug', 'description']
    search_fields = ['name']
    list_per_page = 50
    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'slug', 'description'),
        }),
    )


class AuctionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    list_display = [
        'title', 'seller', 'category', 'starting_price',
        'current_price', 'is_active', 'is_featured',
        'start_time', 'end_time', 'created_at',
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'seller__username', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'description', 'image', 'seller', 'category'),
        }),
        ('Pricing', {
            'fields': ('starting_price', 'current_price', 'reserve_price'),
        }),
        ('Dates', {
            'fields': ('start_time', 'end_time', 'created_at'),
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured'),
        }),
    )


class BidAdmin(admin.ModelAdmin):
    list_display = ['auction', 'bidder', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['auction__title', 'bidder__username']
    readonly_fields = ['created_at']
    list_per_page = 20


admin_site.register(Category, CategoryAdmin)
admin_site.register(Auction, AuctionAdmin)
admin_site.register(Bid, BidAdmin)
