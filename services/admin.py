from django.contrib import admin
from .models import (
    ServiceCategory, Service, SubCategory,
    ServiceProvider, Order, OrderItem,
    Organizer, OrganizerWork, Event,
    EventRequest, ContactMessage,
    Wallet, WalletTransaction, PayoutRequest,
    Milestone, Coupon, Referral, Payment
)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'price', 'created_at')
    list_filter = ('category', 'provider')
    search_fields = ('title', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    fields = ('user', 'status')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'id')

class OrganizerWorkInline(admin.TabularInline):
    model = OrganizerWork
    extra = 1

@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'bio')
    inlines = [OrganizerWorkInline]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'view_organizers')
    list_filter = ('date',)
    search_fields = ('title',)

    def view_organizers(self, obj):
        return ", ".join([o.name for o in obj.organizers.all()])
    view_organizers.short_description = "Organizers"

@admin.register(EventRequest)
class EventRequestAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'client_name', 'date', 'submitted_at')
    list_filter = ('date', 'submitted_at')
    search_fields = ('event_name', 'client_name', 'email')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'available_balance', 'locked_balance')
    search_fields = ('user__username',)

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('wallet__user__username', 'description')

@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('wallet__user__username',)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'order__id')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'is_active', 'valid_until')
    list_filter = ('is_active', 'valid_until')
    search_fields = ('code',)

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_user', 'reward_amount', 'is_rewarded')
    list_filter = ('is_rewarded',)
    search_fields = ('referrer__username', 'referred_user__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'amount', 'method', 'status', 'paymob_order_id')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('paymob_order_id', 'order__id', 'user__username')
