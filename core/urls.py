from django.urls import path
from . import views
from .views_setup import initial_setup

urlpatterns = [
    # Setup page (must be first)
    path('setup/', initial_setup, name='initial_setup'),
    
    # Main Pages
    path('', views.index, name='index'),
    path('stores/', views.stores, name='stores'),
    path('store/<slug:slug>/', views.store_detail, name='store_detail'),
    path('coupons/', views.coupons, name='coupons'),
    path('category/<slug:slug>/', views.category_coupons, name='category_coupons'),
    path('search/', views.search, name='search'),
    
    # User Actions
    path('copy-coupon/<int:coupon_id>/', views.copy_coupon, name='copy_coupon'),
    path('toggle-favorite/<int:coupon_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('notifications/', views.notifications, name='notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Static Pages
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
    
    # Language
    path('set-language/<str:lang>/', views.set_language, name='set_language'),
    
    # API
    path('api/search/', views.api_search, name='api_search'),
    path('api/notifications/count/', views.get_unread_notifications_count, name='notifications_count'),
]