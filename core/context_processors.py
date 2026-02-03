from .models import AppSettings, Category, UserNotification


def global_settings(request):
    settings = AppSettings.get_settings()
    categories = Category.objects.filter(is_active=True)[:10]
    
    # Get current language
    lang = request.session.get('language', settings.default_language)
    
    # Get unread notifications count
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    
    return {
        'app_settings': settings,
        'global_categories': categories,
        'current_language': lang,
        'is_rtl': lang == 'ar',
        'unread_notifications_count': unread_notifications,
    }