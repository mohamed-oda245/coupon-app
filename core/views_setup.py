from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import AppSettings


def is_setup_complete():
    """Check if initial setup is done"""
    return User.objects.filter(is_superuser=True).exists()


def initial_setup(request):
    """First-time setup page"""
    
    # لو الإعداد تم، حوّل للصفحة الرئيسية
    if is_setup_complete():
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        app_name = request.POST.get('app_name', 'كوبونات').strip()
        app_name_en = request.POST.get('app_name_en', 'Coupons').strip()
        
        # التحقق من البيانات
        errors = []
        
        if not username:
            errors.append('اسم المستخدم مطلوب')
        elif len(username) < 3:
            errors.append('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
            
        if not email:
            errors.append('البريد الإلكتروني مطلوب')
            
        if not password1:
            errors.append('كلمة المرور مطلوبة')
        elif len(password1) < 8:
            errors.append('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        elif password1 != password2:
            errors.append('كلمات المرور غير متطابقة')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'core/initial_setup.html', {
                'username': username,
                'email': email,
                'app_name': app_name,
                'app_name_en': app_name_en,
            })
        
        try:
            # إنشاء المستخدم الرئيسي
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password1
            )
            
            # إنشاء إعدادات التطبيق
            settings, created = AppSettings.objects.get_or_create(pk=1)
            settings.app_name = app_name
            settings.app_name_en = app_name_en
            settings.primary_color = '#27ae60'
            settings.secondary_color = '#2c3e50'
            settings.enable_registration = True
            settings.enable_favorites = True
            settings.enable_notifications = True
            settings.enable_english = True
            settings.save()
            
            messages.success(request, '✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return render(request, 'core/initial_setup.html')
    
    return render(request, 'core/initial_setup.html', {
        'app_name': 'كوبونات',
        'app_name_en': 'Coupons',
    })