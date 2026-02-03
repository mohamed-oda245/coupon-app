from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import path
from django.shortcuts import render
from django.contrib.admin import AdminSite
from .models import (
    Category, Store, Coupon, SliderItem, Favorite,
    Notification, UserNotification, AppSettings, CouponUsage,
    UserProfile, ContactMessage
)


# ==================== Guide View ====================
def admin_guide_view(request):
    """صفحة دليل الاستخدام"""
    return render(request, 'admin/guide.html')


# ==================== Category Admin ====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'icon_preview', 'order', 'is_active', 'coupons_count']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['order']
    
    fieldsets = (
        ('📂 معلومات القسم', {
            'fields': ('name', 'name_en', 'slug'),
            'description': '💡 أدخل اسم القسم بالعربي والإنجليزي. الرابط (slug) يتم إنشاؤه تلقائياً.'
        }),
        ('🎨 المظهر', {
            'fields': ('icon', 'image'),
            'description': '💡 الأيقونة: استخدم أيقونات Font Awesome مثل: fas fa-laptop, fas fa-tshirt'
        }),
        ('⚙️ الإعدادات', {
            'fields': ('order', 'is_active'),
            'description': '💡 الترتيب: رقم أصغر = يظهر أولاً. فعّل "نشط" ليظهر في الموقع.'
        }),
    )
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}" style="font-size: 20px; color: #27ae60;"></i>', obj.icon)
        return "—"
    icon_preview.short_description = 'الأيقونة'
    
    def coupons_count(self, obj):
        count = obj.active_coupons_count
        return format_html('<span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>', count)
    coupons_count.short_description = 'الكوبونات'


# ==================== Store Admin ====================
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['logo_preview', 'name', 'is_featured', 'is_active', 'coupons_count', 'click_count', 'order']
    list_filter = ['is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'name_en']
    list_editable = ['is_featured', 'is_active', 'order']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['order', '-is_featured']
    readonly_fields = ['click_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('🏪 معلومات المتجر', {
            'fields': ('name', 'name_en', 'slug', 'url'),
            'description': '💡 أدخل اسم المتجر ورابط الموقع الرسمي للمتجر.'
        }),
        ('🖼️ الصور', {
            'fields': ('logo', 'cover_image'),
            'description': '💡 الشعار: صورة مربعة (مثال: 200x200). الغلاف: صورة عريضة (مثال: 1200x400).'
        }),
        ('📝 الوصف', {
            'fields': ('description', 'description_en'),
            'description': '💡 وصف قصير عن المتجر يظهر في صفحة المتجر.',
            'classes': ('collapse',)
        }),
        ('⚙️ الإعدادات', {
            'fields': ('is_featured', 'is_active', 'order'),
            'description': '💡 "متجر مميز" يظهر في الصفحة الرئيسية. الترتيب: رقم أصغر = يظهر أولاً.'
        }),
        ('📊 الإحصائيات', {
            'fields': ('click_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 8px; object-fit: contain; background: #f8f9fa;" />', obj.logo.url)
        return format_html('<span style="color: #ccc;"><i class="fas fa-store"></i></span>')
    logo_preview.short_description = 'الشعار'
    
    def coupons_count(self, obj):
        count = obj.active_coupons_count
        color = '#27ae60' if count > 0 else '#ccc'
        return format_html('<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>', color, count)
    coupons_count.short_description = 'الكوبونات'


# ==================== Coupon Admin ====================
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['title_short', 'store', 'code_display', 'discount_display', 'status_badges', 'used_count', 'is_active']
    list_filter = ['is_active', 'is_best_offer', 'is_most_used', 'store', 'category', 'created_at']
    search_fields = ['title', 'code', 'store__name']
    list_editable = ['is_active']
    autocomplete_fields = ['store', 'category']
    readonly_fields = ['used_count', 'view_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('🎫 معلومات الكوبون', {
            'fields': ('store', 'category', 'title', 'title_en', 'code'),
            'description': '💡 اختر المتجر، ثم أدخل عنوان جذاب للكوبون وكود الخصم.'
        }),
        ('💰 الخصم', {
            'fields': ('discount_percentage', 'discount_value'),
            'description': '💡 أدخل نسبة الخصم (مثال: 20) أو قيمة الخصم الثابتة.'
        }),
        ('📝 الوصف', {
            'fields': ('description', 'description_en'),
            'description': '💡 وصف اختياري يوضح تفاصيل العرض.',
            'classes': ('collapse',)
        }),
        ('🔗 الروابط والصور', {
            'fields': ('image', 'affiliate_url'),
            'description': '💡 رابط الأفلييت: الرابط الذي سيذهب إليه المستخدم عند نسخ الكود.',
            'classes': ('collapse',)
        }),
        ('🏷️ التصنيفات', {
            'fields': ('is_active', 'is_best_offer', 'is_most_used', 'is_exclusive', 'is_verified', 'expiry_date'),
            'description': '''💡 التصنيفات:
            • أفضل عرض: يظهر في قسم "أفضل الكوبونات"
            • الأكثر استخداماً: يظهر في قسم "الأكثر استخداماً"
            • حصري: يظهر بعلامة "حصري"
            • موثق: يظهر بعلامة "✓ موثق"'''
        }),
        ('📊 الإحصائيات', {
            'fields': ('used_count', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        title = obj.title[:30] + '...' if len(obj.title) > 30 else obj.title
        return title
    title_short.short_description = 'العنوان'
    
    def code_display(self, obj):
        return format_html(
            '<code style="background: #f8f9fa; padding: 5px 10px; border-radius: 5px; '
            'border: 1px dashed #27ae60; font-weight: bold;">{}</code>', 
            obj.code
        )
    code_display.short_description = 'الكود'
    
    def discount_display(self, obj):
        if obj.discount_percentage:
            return format_html(
                '<span style="background: #e74c3c; color: white; padding: 3px 10px; '
                'border-radius: 10px; font-weight: bold;">{}%</span>', 
                obj.discount_percentage
            )
        return "—"
    discount_display.short_description = 'الخصم'
    
    def status_badges(self, obj):
        badges = []
        if obj.is_best_offer:
            badges.append('<span style="background: #f39c12; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin: 1px;">⭐ أفضل</span>')
        if obj.is_most_used:
            badges.append('<span style="background: #e74c3c; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin: 1px;">🔥 رائج</span>')
        if obj.is_exclusive:
            badges.append('<span style="background: #9b59b6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin: 1px;">💎 حصري</span>')
        return format_html(' '.join(badges)) if badges else '—'
    status_badges.short_description = 'التصنيف'


# ==================== Slider Admin ====================
@admin.register(SliderItem)
class SliderItemAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'order', 'is_active', 'click_count']
    list_filter = ['is_active']
    search_fields = ['title', 'title_en']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    readonly_fields = ['click_count', 'created_at']
    
    fieldsets = (
        ('📝 المحتوى', {
            'fields': ('title', 'title_en', 'subtitle', 'subtitle_en'),
            'description': '💡 العنوان الرئيسي والفرعي للسلايدر.'
        }),
        ('🖼️ الصورة والرابط', {
            'fields': ('image', 'link', 'button_text', 'button_text_en'),
            'description': '💡 الصورة المفضلة: 1200x400 بكسل. الرابط: الصفحة التي سينتقل إليها الزائر.'
        }),
        ('⚙️ الإعدادات', {
            'fields': ('order', 'is_active'),
            'description': '💡 الترتيب: رقم أصغر = يظهر أولاً.'
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 50px; border-radius: 5px; object-fit: cover;" />', obj.image.url)
        return format_html('<span style="background: linear-gradient(135deg, #27ae60, #2c3e50); display: inline-block; width: 100px; height: 50px; border-radius: 5px;"></span>')
    image_preview.short_description = 'الصورة'


# ==================== Notification Admin ====================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'send_to_all', 'is_sent', 'sent_badge', 'read_count', 'created_at']
    list_filter = ['is_sent', 'send_to_all', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['is_sent', 'sent_at', 'read_count', 'created_at']
    
    fieldsets = (
        ('📝 محتوى الإشعار', {
            'fields': ('title', 'title_en', 'message', 'message_en'),
            'description': '💡 اكتب عنوان ورسالة الإشعار الذي سيصل للمستخدمين.'
        }),
        ('🔗 الإضافات', {
            'fields': ('image', 'link', 'target_store'),
            'description': '💡 يمكنك إضافة صورة ورابط للإشعار (اختياري).',
            'classes': ('collapse',)
        }),
        ('📤 الإرسال', {
            'fields': ('send_to_all',),
            'description': '💡 فعّل "إرسال للجميع" لإرسال الإشعار لكل المستخدمين.'
        }),
        ('📊 معلومات الإرسال', {
            'fields': ('is_sent', 'sent_at', 'read_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_notifications']
    
    def sent_badge(self, obj):
        if obj.is_sent:
            return format_html('<span style="background: #27ae60; color: white; padding: 3px 10px; border-radius: 10px;">✓ تم الإرسال</span>')
        return format_html('<span style="background: #f39c12; color: white; padding: 3px 10px; border-radius: 10px;">⏳ في الانتظار</span>')
    sent_badge.short_description = 'الحالة'
    
    def send_notifications(self, request, queryset):
        count = 0
        for notification in queryset.filter(is_sent=False):
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            count += 1
        self.message_user(request, f'✅ تم إرسال {count} إشعار بنجاح!')
    send_notifications.short_description = '📤 إرسال الإشعارات المحددة'


# ==================== App Settings Admin ====================
@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('📱 معلومات التطبيق', {
            'fields': ('app_name', 'app_name_en', 'app_logo', 'favicon', 'app_description', 'app_description_en'),
            'description': '💡 المعلومات الأساسية للتطبيق والموقع.'
        }),
        ('🎨 الألوان', {
            'fields': ('primary_color', 'secondary_color', 'accent_color'),
            'description': '💡 اختر الألوان الرئيسية للتطبيق. استخدم أكواد HEX مثل: #27ae60'
        }),
        ('🌐 اللغة', {
            'fields': ('default_language', 'enable_english'),
            'description': '💡 اللغة الافتراضية وإمكانية تفعيل اللغة الإنجليزية.'
        }),
        ('📱 روابط التطبيقات', {
            'fields': ('play_store_url', 'app_store_url'),
            'description': '💡 روابط تحميل التطبيق من المتاجر (ستظهر في الموقع).'
        }),
        ('📲 السوشيال ميديا', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'tiktok_url', 'youtube_url', 'whatsapp_number'),
            'description': '💡 روابط حساباتك على مواقع التواصل الاجتماعي.',
            'classes': ('collapse',)
        }),
        ('📞 التواصل', {
            'fields': ('contact_email', 'contact_phone'),
            'description': '💡 معلومات التواصل التي ستظهر في صفحة "اتصل بنا".'
        }),
        ('📄 الصفحات', {
            'fields': ('about_text', 'about_text_en', 'privacy_policy', 'privacy_policy_en', 'terms_conditions', 'terms_conditions_en'),
            'description': '💡 محتوى الصفحات الثابتة (من نحن، سياسة الخصوصية، الشروط).',
            'classes': ('collapse',)
        }),
        ('⚙️ إعدادات العرض', {
            'fields': ('coupons_per_page', 'stores_per_page'),
            'description': '💡 عدد العناصر في كل صفحة.'
        }),
        ('🔧 الميزات', {
            'fields': ('enable_registration', 'enable_favorites', 'enable_notifications'),
            'description': '💡 تفعيل أو تعطيل ميزات معينة.'
        }),
        ('🔧 الصيانة', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'description': '💡 تفعيل وضع الصيانة يمنع الزوار من الدخول.',
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not AppSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ==================== Other Admins ====================
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'coupon__title']
    readonly_fields = ['created_at']


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'action', 'device_type', 'created_at']
    list_filter = ['action', 'device_type', 'created_at']
    search_fields = ['coupon__code', 'user__username']
    readonly_fields = ['coupon', 'user', 'action', 'ip_address', 'user_agent', 'device_type', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'preferred_language', 'is_banned', 'created_at']
    list_filter = ['preferred_language', 'is_banned', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'read_badge', 'replied_badge', 'created_at']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('📧 معلومات المرسل', {
            'fields': ('name', 'email', 'phone', 'created_at')
        }),
        ('💬 الرسالة', {
            'fields': ('subject', 'message')
        }),
        ('↩️ الرد', {
            'fields': ('is_read', 'is_replied', 'reply_message', 'replied_at'),
            'description': '💡 اكتب ردك وفعّل "تم الرد" عند الإرسال.'
        }),
    )
    
    def read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color: #27ae60;">✓ مقروءة</span>')
        return format_html('<span style="color: #e74c3c; font-weight: bold;">● جديدة</span>')
    read_badge.short_description = 'الحالة'
    
    def replied_badge(self, obj):
        if obj.is_replied:
            return format_html('<span style="color: #27ae60;">✓ تم الرد</span>')
        return format_html('<span style="color: #f39c12;">⏳ بانتظار الرد</span>')
    replied_badge.short_description = 'الرد'


# ==================== Custom Admin URLs ====================
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('guide/', self.admin_view(admin_guide_view), name='admin_guide'),
        ]
        return custom_urls + urls


# ==================== Admin Site Config ====================
admin.site.site_header = '🎫 لوحة تحكم الكوبونات'
admin.site.site_title = 'إدارة الكوبونات'
admin.site.index_title = 'مرحباً بك في لوحة التحكم'