from django.contrib import admin
from auction_project.admin import admin_site
from .models import Payment, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ['type', 'amount', 'description', 'created_at']


class PaymentAdmin(admin.ModelAdmin):
    inlines = [TransactionInline]
    list_display = [
        'transaction_id', 'auction', 'buyer', 'seller',
        'amount', 'payment_method', 'status', 'created_at',
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'transaction_id', 'auction__title',
        'buyer__username', 'seller__username',
    ]
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    list_per_page = 20
    fieldsets = (
        ('Payment Info', {
            'fields': ('transaction_id', 'auction', 'buyer', 'seller'),
        }),
        ('Details', {
            'fields': ('amount', 'payment_method', 'status'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'type', 'amount', 'created_at']
    list_filter = ['type', 'created_at']
    readonly_fields = ['created_at']
    list_per_page = 20


admin_site.register(Payment, PaymentAdmin)
admin_site.register(Transaction, TransactionAdmin)
