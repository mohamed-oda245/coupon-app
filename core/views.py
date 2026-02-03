from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import (
    Category, Store, Coupon, SliderItem, Favorite,
    Notification, UserNotification, AppSettings, CouponUsage,
    UserProfile, ContactMessage
)
import json

# اضافة جديدة للتحقق من الاعداد الاولي
from .views_setup import is_setup_complete


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_type(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'mobile' in user_agent or 'android' in user_agent:
        return 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        return 'tablet'
    return 'desktop'


def get_current_language(request):
    return request.session.get('language', 'ar')


def set_language(request, lang):
    if lang in ['ar', 'en']:
        request.session['language'] = lang
    return redirect(request.META.get('HTTP_REFERER', 'index'))


def index(request):
    # التحقق من الاعداد الاولي - تحويل لصفحة الاعداد لو اول مرة
    if not is_setup_complete():
        return redirect('initial_setup')
    
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    if settings.maintenance_mode and not request.user.is_staff:
        return render(request, 'core/maintenance.html', {'settings': settings})
    
    slider_items = SliderItem.objects.filter(is_active=True)[:5]
    best_coupons = Coupon.objects.filter(is_active=True, is_best_offer=True)[:8]
    most_used_coupons = Coupon.objects.filter(is_active=True, is_most_used=True)[:8]
    latest_coupons = Coupon.objects.filter(is_active=True).order_by('-created_at')[:8]
    featured_stores = Store.objects.filter(is_active=True, is_featured=True)[:8]
    categories = Category.objects.filter(is_active=True)[:8]
    
    # Get user favorites
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(request.user.favorites.values_list('coupon_id', flat=True))
    
    context = {
        'settings': settings,
        'lang': lang,
        'slider_items': slider_items,
        'best_coupons': best_coupons,
        'most_used_coupons': most_used_coupons,
        'latest_coupons': latest_coupons,
        'featured_stores': featured_stores,
        'categories': categories,
        'user_favorites': user_favorites,
    }
    return render(request, 'core/index.html', context)


def stores(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    stores_list = Store.objects.filter(is_active=True)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        stores_list = stores_list.filter(
            Q(name__icontains=search_query) | 
            Q(name_en__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(stores_list, settings.stores_per_page)
    page = request.GET.get('page')
    stores_page = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'lang': lang,
        'stores': stores_page,
        'search_query': search_query,
    }
    return render(request, 'core/stores.html', context)


def store_detail(request, slug):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    store = get_object_or_404(Store, slug=slug, is_active=True)
    
    # Increment click count
    store.click_count += 1
    store.save(update_fields=['click_count'])
    
    coupons = store.coupons.filter(is_active=True)
    
    # Get user favorites
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(request.user.favorites.values_list('coupon_id', flat=True))
    
    context = {
        'settings': settings,
        'lang': lang,
        'store': store,
        'coupons': coupons,
        'user_favorites': user_favorites,
    }
    return render(request, 'core/store_detail.html', context)


def coupons(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    coupons_list = Coupon.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    stores_list = Store.objects.filter(is_active=True)
    
    # Filters
    category_slug = request.GET.get('category')
    store_slug = request.GET.get('store')
    search_query = request.GET.get('q', '')
    
    if category_slug:
        coupons_list = coupons_list.filter(category__slug=category_slug)
    
    if store_slug:
        coupons_list = coupons_list.filter(store__slug=store_slug)
    
    if search_query:
        coupons_list = coupons_list.filter(
            Q(title__icontains=search_query) | 
            Q(title_en__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(store__name__icontains=search_query)
        )
    
    # Get user favorites
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(request.user.favorites.values_list('coupon_id', flat=True))
    
    # Pagination
    paginator = Paginator(coupons_list, settings.coupons_per_page)
    page = request.GET.get('page')
    coupons_page = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'lang': lang,
        'coupons': coupons_page,
        'categories': categories,
        'stores': stores_list,
        'category_slug': category_slug,
        'store_slug': store_slug,
        'search_query': search_query,
        'user_favorites': user_favorites,
    }
    return render(request, 'core/coupons.html', context)


def category_coupons(request, slug):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    category = get_object_or_404(Category, slug=slug, is_active=True)
    coupons_list = Coupon.objects.filter(category=category, is_active=True)
    
    # Get user favorites
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(request.user.favorites.values_list('coupon_id', flat=True))
    
    # Pagination
    paginator = Paginator(coupons_list, settings.coupons_per_page)
    page = request.GET.get('page')
    coupons_page = paginator.get_page(page)
    
    context = {
        'settings': settings,
        'lang': lang,
        'category': category,
        'coupons': coupons_page,
        'user_favorites': user_favorites,
    }
    return render(request, 'core/category_coupons.html', context)


@require_POST
def copy_coupon(request, coupon_id):
    try:
        coupon = get_object_or_404(Coupon, id=coupon_id, is_active=True)
        
        # Log usage
        CouponUsage.objects.create(
            coupon=coupon,
            user=request.user if request.user.is_authenticated else None,
            action='copy',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_type=get_device_type(request)
        )
        
        # Increment used count
        coupon.used_count += 1
        coupon.save(update_fields=['used_count'])
        
        return JsonResponse({
            'success': True,
            'code': coupon.code,
            'redirect_url': coupon.get_redirect_url()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def favorites(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    favorites_list = Favorite.objects.filter(user=request.user).select_related('coupon', 'coupon__store')
    
    context = {
        'settings': settings,
        'lang': lang,
        'favorites': favorites_list,
    }
    return render(request, 'core/favorites.html', context)


@login_required
@require_POST
def toggle_favorite(request, coupon_id):
    try:
        coupon = get_object_or_404(Coupon, id=coupon_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            coupon=coupon
        )
        
        if not created:
            favorite.delete()
            return JsonResponse({'success': True, 'action': 'removed'})
        
        return JsonResponse({'success': True, 'action': 'added'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notifications(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    # Get all sent notifications
    all_notifications = Notification.objects.filter(is_sent=True, send_to_all=True)
    
    # Create user notifications if they don't exist
    for notification in all_notifications:
        UserNotification.objects.get_or_create(
            user=request.user,
            notification=notification
        )
    
    user_notifications = UserNotification.objects.filter(
        user=request.user
    ).select_related('notification').order_by('-created_at')
    
    context = {
        'settings': settings,
        'lang': lang,
        'notifications': user_notifications,
    }
    return render(request, 'core/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        user_notification = get_object_or_404(
            UserNotification, 
            id=notification_id, 
            user=request.user
        )
        user_notification.is_read = True
        user_notification.read_at = timezone.now()
        user_notification.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def search(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    query = request.GET.get('q', '')
    
    coupons_results = []
    stores_results = []
    
    if query:
        coupons_results = Coupon.objects.filter(
            Q(title__icontains=query) |
            Q(title_en__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )[:20]
        
        stores_results = Store.objects.filter(
            Q(name__icontains=query) |
            Q(name_en__icontains=query),
            is_active=True
        )[:10]
    
    # Get user favorites
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(request.user.favorites.values_list('coupon_id', flat=True))
    
    context = {
        'settings': settings,
        'lang': lang,
        'query': query,
        'coupons': coupons_results,
        'stores': stores_results,
        'user_favorites': user_favorites,
    }
    return render(request, 'core/search.html', context)


# Auth Views
def register_view(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    if not settings.enable_registration:
        messages.error(request, 'التسجيل مغلق حالياً' if lang == 'ar' else 'Registration is closed')
        return redirect('index')
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'كلمات المرور غير متطابقة' if lang == 'ar' else 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود مسبقاً' if lang == 'ar' else 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مسجل مسبقاً' if lang == 'ar' else 'Email already registered')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح!' if lang == 'ar' else 'Account created successfully!')
            return redirect('index')
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'registration/register.html', context)


def login_view(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'profile') and user.profile.is_banned:
                messages.error(request, 'حسابك محظور' if lang == 'ar' else 'Your account is banned')
            else:
                login(request, user)
                messages.success(request, 'تم تسجيل الدخول بنجاح!' if lang == 'ar' else 'Logged in successfully!')
                return redirect(request.GET.get('next', 'index'))
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة' if lang == 'ar' else 'Invalid username or password')
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'registration/login.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح!')
    return redirect('index')


@login_required
def profile(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        
        # Update user info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile
        profile.phone = request.POST.get('phone', '')
        profile.preferred_language = request.POST.get('language', 'ar')
        profile.receive_notifications = request.POST.get('notifications') == 'on'
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'تم تحديث الملف الشخصي بنجاح!' if lang == 'ar' else 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'core/profile.html', context)


# Static Pages
def about(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'core/about.html', context)


def privacy(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'core/privacy.html', context)


def terms(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'core/terms.html', context)


def contact(request):
    settings = AppSettings.get_settings()
    lang = get_current_language(request)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        
        messages.success(request, 'تم إرسال رسالتك بنجاح!' if lang == 'ar' else 'Message sent successfully!')
        return redirect('contact')
    
    context = {
        'settings': settings,
        'lang': lang,
    }
    return render(request, 'core/contact.html', context)


# API Views for AJAX
def api_search(request):
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    coupons = Coupon.objects.filter(
        Q(title__icontains=query) |
        Q(code__icontains=query) |
        Q(store__name__icontains=query),
        is_active=True
    )[:5]
    
    stores = Store.objects.filter(
        Q(name__icontains=query) |
        Q(name_en__icontains=query),
        is_active=True
    )[:3]
    
    results = []
    
    for coupon in coupons:
        results.append({
            'type': 'coupon',
            'title': coupon.title,
            'code': coupon.code,
            'store': coupon.store.name,
            'discount': coupon.discount_percentage,
            'url': f'/coupons/?q={coupon.code}'
        })
    
    for store in stores:
        results.append({
            'type': 'store',
            'title': store.name,
            'logo': store.logo.url if store.logo else '',
            'url': f'/store/{store.slug}/'
        })
    
    return JsonResponse({'results': results})


def get_unread_notifications_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    
    count = UserNotification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})