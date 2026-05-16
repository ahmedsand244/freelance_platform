from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from pages.views import about_view

urlpatterns = [
    # ── Core ──
    path('', views.home, name='home'),

    # ── Services ──
    path('all/', views.services_list_view, name='services_list'),
    path('category/<int:category_id>/', views.subcategories_view, name='subcategories'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_services_view, name='subcategory_services'),
    path('service/<int:service_id>/', views.service_detail_view, name='service_detail'),
    path('service/add/', views.add_service_view, name='add_service'),
    path('service/add/ai-generate/', views.generate_ai_description_view, name='generate_ai_description'),
    path('search/', views.search_services, name='search_services'),
    path('search/autocomplete/', views.autocomplete_search, name='search_autocomplete'),

    # ── Wishlist ──
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:service_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # ── Cart & Checkout ──
    path('cart/add/<int:service_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),

    # ── Checkout & Coupons ──
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/apply-coupon/', views.apply_coupon_view, name='apply_coupon'),

    # ── Orders ──
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('order/<int:order_id>/chat/create-offer/', views.create_custom_offer_view, name='create_custom_offer'),
    path('order/<int:order_id>/chat/', views.order_chat_view, name='order_chat'),
    path('order/<int:order_id>/chat/api/', views.order_chat_api, name='order_chat_api'),
    path('order/<int:order_id>/revision/', views.request_revision_view, name='request_revision'),
    path('order/<int:order_id>/accept-delivery/', views.accept_delivery_view, name='accept_delivery'),
    path('payment/process-remaining/<int:order_id>/', views.process_remaining_payment_view, name='process_remaining_payment'),
    
    # ── Custom Offers ──
    path('custom-offer/<int:offer_id>/accept/', views.accept_custom_offer_view, name='accept_custom_offer'),

    # ── Order Tasks (Progress Tracker) ──
    path('order/<int:order_id>/task/add/', views.add_order_task_view, name='add_order_task'),
    path('task/<int:task_id>/toggle/', views.toggle_order_task_view, name='toggle_order_task'),
    path('task/<int:task_id>/delete/', views.delete_order_task_view, name='delete_order_task'),

    # ── Order Drafts (Draft Submissions) ──
    path('order/<int:order_id>/draft/upload/', views.upload_order_draft_view, name='upload_order_draft'),
    path('draft/<int:draft_id>/delete/', views.delete_order_draft_view, name='delete_order_draft'),

    # ── Order Updates (Activity Feed) ──
    path('order/<int:order_id>/update/', views.post_order_update_view, name='post_order_update'),

    # ── Buyer Requests / Marketplace ──
    path('projects/post/', views.post_project_view, name='post_project'),
    path('projects/', views.buyer_requests_list_view, name='buyer_requests_list'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/bid/<int:bid_id>/award/', views.award_bid_view, name='award_bid'),

    # ── Payment ──
    path('payment/method/<int:order_id>/', views.payment_method_view, name='payment_method'),
    path('payment/process/<int:order_id>/', views.process_payment_view, name='process_payment'),
    path('payment/callback/', views.payment_callback_view, name='payment_callback'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('payment/failed/', views.payment_failed_view, name='payment_failed'),

    # ── Account / Dashboard ──
    path('my-account/', views.my_account_view, name='my_account'),
    path('account/update/', views.update_account, name='update_account'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='password_change'),

    # ── Seller Profile & Portfolio ──
    path('seller/<str:username>/', views.seller_profile_view, name='seller_profile'),
    path('my-account/portfolio/', views.manage_portfolio_view, name='manage_portfolio'),
    path('my-account/portfolio/add/', views.add_portfolio_item_view, name='add_portfolio_item'),

    # ── Wallet ──
    path('my-account/wallet/', views.wallet_view, name='wallet'),
    path('my-account/wallet/request-payout/', views.request_payout_view, name='request_payout'),

    # ── Notifications ──
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/count/', views.notifications_count, name='notifications_count'),

    # ── Admin ──
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/dashboard/payout/<int:payout_id>/', views.admin_approve_payout_view, name='admin_approve_payout'),
    path('admin/approve-service/<int:service_id>/', views.admin_approve_service_view, name='admin_approve_service'),
    path('admin/approve-event/<int:request_id>/', views.admin_approve_event_view, name='admin_approve_event'),
    path('admin/update-order-status/<int:order_id>/', views.update_order_status_view, name='update_order_status'),
    path('admin/order/<int:order_id>/', views.admin_order_detail_view, name='admin_order_detail'),

    # ── Organizers ──
    path('events/', views.events_view, name='events'),
    path('events/request/', views.event_request_view, name='event_request'),
    path('organizer/<int:organizer_id>/', views.organizer_detail_view, name='organizer_detail'),
    path('organizer/<int:organizer_id>/contact/', views.contact_organizer_view, name='contact_organizer'),
    path('organizers/<int:organizer_id>/', views.organizer_profile_view, name='organizer_profile'),
    path('organizers/', views.all_organizers_view, name='all_organizers'),

    # ── Misc ──
    path('contact/', views.contact_view, name='contact'),
    path('about/', about_view, name='services-about'),
    path('chat/', views.chatbot_response_view, name='chatbot_response'),
]
