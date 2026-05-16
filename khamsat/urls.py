from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

def force_google_login(request):
    return redirect("/accounts/google/login/?process=login")
# هذا المسار خاص بتغيير اللغة
from services import views as services_views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # Payment callback should be accessible without language prefix for Paymob
    path('services/payment-callback/', services_views.payment_callback_view, name='payment_callback_no_i18n'),
]

# المسارات الرئيسية داخل i18n_patterns عشان الترجمة تشتغل عليها
from pages import views as pages_views

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('game/', pages_views.game_view, name='game'),
    path('services/', include('services.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),

    path('ar/accounts/google/login/', force_google_login),
    path('en/accounts/google/login/', force_google_login),
)

# الملفات الثابتة والميديا
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
