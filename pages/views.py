# from django.shortcuts import render
# from .models import TeamMember, Partner

# def home_view(request):
#     return render(request, 'pages/home.html')

# def contact_view(request):
#     return render(request, 'pages/contact.html')

# def about_view(request):
#     team_members = TeamMember.objects.all()
#     partners = Partner.objects.all()
#     return render(request, 'pages/about.html', {
#         'team_members': team_members,
#         'partners': partners,
#     })





from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import TeamMember, Partner

def home_view(request):
    return redirect('/services/')

def contact_view(request):
    return render(request, 'pages/contact.html')

def about_view(request):
    team_members = TeamMember.objects.all()
    partners = Partner.objects.all()
    return render(request, 'pages/about.html', {
        'team_members': team_members,
        'partners': partners,
    })

def terms_view(request):
    return render(request, 'pages/terms.html')

def privacy_view(request):
    return render(request, 'pages/privacy.html')

from django.db.models import Sum, Count, Avg
from services.models import Service, Order, Payment, ServiceCategory, ServiceProvider

def refund_view(request):
    return render(request, 'pages/refund.html')

def game_view(request):
    return render(request, 'pages/game.html')

def pulse_view(request):
    # Total Market Liquidity
    total_revenue = Payment.objects.filter(status__in=['paid', 'released']).aggregate(sum=Sum('amount'))['sum'] or 0
    # Success Ecosystem Stats
    active_services = Service.objects.filter(is_active=True).count()
    success_orders = Order.objects.filter(status='completed').count()
    expert_force = ServiceProvider.objects.filter(is_verified=True).count()
    # Market Dominance (Category Distribution)
    categories_stats = ServiceCategory.objects.annotate(count=Count('services')).order_by('-count')[:6]
    
    context = {
        'total_revenue': total_revenue,
        'active_services': active_services,
        'success_orders': success_orders,
        'expert_force': expert_force,
        'categories_stats': categories_stats,
    }
    return render(request, 'pages/pulse.html', context)

def legends_view(request):
    # Fetch High-Performance 'Legendary' services (Rating 4.8+)
    legend_services = Service.objects.annotate(rating_val=Avg('reviews__rating'))\
                                     .filter(rating_val__gte=4.8, is_active=True)\
                                     .order_by('-rating_val')[:12]
    return render(request, 'pages/legends.html', {'legends': legend_services})

from django.utils.translation import gettext as _

def referral_redirect(request, username):
    User = get_user_model()
    try:
        referrer = User.objects.get(username__iexact=username)
        if request.user.is_authenticated and request.user == referrer:
            pass
        else:
            request.session['intended_referrer'] = referrer.id
            messages.success(request, _("You were referred by {username}! Create an account to claim benefits.").format(username=referrer.username))
    except User.DoesNotExist:
        pass
    return redirect('account_signup')



