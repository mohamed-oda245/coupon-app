from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField('الاسم بالعربي', max_length=100)
    name_en = models.CharField('الاسم بالإنجليزي', max_length=100, blank=True)
    slug = models.SlugField('الرابط', unique=True, allow_unicode=True)
    icon = models.CharField('الأيقونة (Font Awesome)', max_length=50, blank=True, help_text='مثال: fas fa-shopping-bag')
    image = models.ImageField('صورة القسم', upload_to='categories/', blank=True, null=True)
    order = models.PositiveIntegerField('الترتيب', default=0)
    is_active = models.BooleanField('نشط', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_name(self, lang='ar'):
        if lang == 'en' and self.name_en:
            return self.name_en
        return self.name

    @property
    def active_coupons_count(self):
        return self.coupons.filter(is_active=True).count()


class Store(models.Model):
    name = models.CharField('اسم المتجر بالعربي', max_length=100)
    name_en = models.CharField('اسم المتجر بالإنجليزي', max_length=100, blank=True)
    slug = models.SlugField('الرابط', unique=True, allow_unicode=True)
    logo = models.ImageField('شعار المتجر', upload_to='stores/', blank=True, null=True)
    cover_image = models.ImageField('صورة الغلاف', upload_to='stores/covers/', blank=True, null=True)
    url = models.URLField('رابط المتجر')
    description = models.TextField('الوصف بالعربي', blank=True)
    description_en = models.TextField('الوصف بالإنجليزي', blank=True)
    is_featured = models.BooleanField('متجر مميز', default=False)
    is_active = models.BooleanField('نشط', default=True)
    order = models.PositiveIntegerField('الترتيب', default=0)
    click_count = models.PositiveIntegerField('عدد الزيارات', default=0)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'متجر'
        verbose_name_plural = 'المتاجر'
        ordering = ['order', '-is_featured', 'name']

    def __str__(self):
        return self.name

    def get_name(self, lang='ar'):
        if lang == 'en' and self.name_en:
            return self.name_en
        return self.name

    def get_description(self, lang='ar'):
        if lang == 'en' and self.description_en:
            return self.description_en
        return self.description

    @property
    def active_coupons_count(self):
        return self.coupons.filter(is_active=True).count()


class Coupon(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='coupons', verbose_name='المتجر')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupons', verbose_name='القسم')
    title = models.CharField('العنوان بالعربي', max_length=200)
    title_en = models.CharField('العنوان بالإنجليزي', max_length=200, blank=True)
    code = models.CharField('كود الخصم', max_length=50)
    discount_percentage = models.PositiveIntegerField('نسبة الخصم %', default=0)
    discount_value = models.DecimalField('قيمة الخصم', max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField('الوصف بالعربي', blank=True)
    description_en = models.TextField('الوصف بالإنجليزي', blank=True)
    image = models.ImageField('صورة الكوبون', upload_to='coupons/', blank=True, null=True)
    affiliate_url = models.URLField('رابط الأفلييت', blank=True)
    expiry_date = models.DateField('تاريخ الانتهاء', null=True, blank=True)
    is_active = models.BooleanField('نشط', default=True)
    is_best_offer = models.BooleanField('أفضل عرض', default=False)
    is_most_used = models.BooleanField('الأكثر استخداماً', default=False)
    is_exclusive = models.BooleanField('حصري', default=False)
    is_verified = models.BooleanField('موثق', default=True)
    used_count = models.PositiveIntegerField('عدد مرات الاستخدام', default=0)
    view_count = models.PositiveIntegerField('عدد المشاهدات', default=0)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'كوبون'
        verbose_name_plural = 'الكوبونات'
        ordering = ['-is_best_offer', '-is_most_used', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.store.name}"

    def get_title(self, lang='ar'):
        if lang == 'en' and self.title_en:
            return self.title_en
        return self.title

    def get_description(self, lang='ar'):
        if lang == 'en' and self.description_en:
            return self.description_en
        return self.description

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None

    def get_redirect_url(self):
        if self.affiliate_url:
            return self.affiliate_url
        return self.store.url


class SliderItem(models.Model):
    title = models.CharField('العنوان بالعربي', max_length=200)
    title_en = models.CharField('العنوان بالإنجليزي', max_length=200, blank=True)
    subtitle = models.CharField('العنوان الفرعي', max_length=300, blank=True)
    subtitle_en = models.CharField('العنوان الفرعي بالإنجليزي', max_length=300, blank=True)
    image = models.ImageField('الصورة', upload_to='slider/', blank=True, null=True)
    link = models.URLField('الرابط', blank=True)
    button_text = models.CharField('نص الزر', max_length=50, default='تسوق الآن')
    button_text_en = models.CharField('نص الزر بالإنجليزي', max_length=50, default='Shop Now')
    order = models.PositiveIntegerField('الترتيب', default=0)
    is_active = models.BooleanField('نشط', default=True)
    click_count = models.PositiveIntegerField('عدد النقرات', default=0)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'عنصر سلايدر'
        verbose_name_plural = 'السلايدر'
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_title(self, lang='ar'):
        if lang == 'en' and self.title_en:
            return self.title_en
        return self.title

    def get_subtitle(self, lang='ar'):
        if lang == 'en' and self.subtitle_en:
            return self.subtitle_en
        return self.subtitle

    def get_button_text(self, lang='ar'):
        if lang == 'en' and self.button_text_en:
            return self.button_text_en
        return self.button_text


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='المستخدم')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='الكوبون')
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)

    class Meta:
        verbose_name = 'مفضلة'
        verbose_name_plural = 'المفضلات'
        unique_together = ('user', 'coupon')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.coupon.title}"


class Notification(models.Model):
    title = models.CharField('العنوان بالعربي', max_length=200)
    title_en = models.CharField('العنوان بالإنجليزي', max_length=200, blank=True)
    message = models.TextField('الرسالة بالعربي')
    message_en = models.TextField('الرسالة بالإنجليزي', blank=True)
    image = models.ImageField('صورة الإشعار', upload_to='notifications/', blank=True, null=True)
    link = models.URLField('الرابط', blank=True)
    target_store = models.ForeignKey(Store, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='متجر محدد')
    send_to_all = models.BooleanField('إرسال للجميع', default=True)
    is_sent = models.BooleanField('تم الإرسال', default=False)
    sent_at = models.DateTimeField('تاريخ الإرسال', null=True, blank=True)
    read_count = models.PositiveIntegerField('عدد القراءات', default=0)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_title(self, lang='ar'):
        if lang == 'en' and self.title_en:
            return self.title_en
        return self.title

    def get_message(self, lang='ar'):
        if lang == 'en' and self.message_en:
            return self.message_en
        return self.message


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='المستخدم')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications', verbose_name='الإشعار')
    is_read = models.BooleanField('مقروء', default=False)
    read_at = models.DateTimeField('تاريخ القراءة', null=True, blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'إشعار مستخدم'
        verbose_name_plural = 'إشعارات المستخدمين'
        unique_together = ('user', 'notification')
        ordering = ['-created_at']


class AppSettings(models.Model):
    app_name = models.CharField('اسم التطبيق بالعربي', max_length=100, default='كوبونات')
    app_name_en = models.CharField('اسم التطبيق بالإنجليزي', max_length=100, default='Coupons')
    app_logo = models.ImageField('شعار التطبيق', upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField('أيقونة المتصفح', upload_to='settings/', blank=True, null=True)
    app_description = models.TextField('وصف التطبيق بالعربي', blank=True)
    app_description_en = models.TextField('وصف التطبيق بالإنجليزي', blank=True)
    
    # Colors
    primary_color = models.CharField('اللون الأساسي', max_length=7, default='#27ae60')
    secondary_color = models.CharField('اللون الثانوي', max_length=7, default='#2c3e50')
    accent_color = models.CharField('لون التمييز', max_length=7, default='#f39c12')
    
    # Language
    default_language = models.CharField('اللغة الافتراضية', max_length=2, choices=[('ar', 'العربية'), ('en', 'English')], default='ar')
    enable_english = models.BooleanField('تفعيل الإنجليزية', default=True)
    
    # Social Media
    facebook_url = models.URLField('فيسبوك', blank=True)
    twitter_url = models.URLField('تويتر', blank=True)
    instagram_url = models.URLField('انستقرام', blank=True)
    tiktok_url = models.URLField('تيك توك', blank=True)
    youtube_url = models.URLField('يوتيوب', blank=True)
    whatsapp_number = models.CharField('واتساب', max_length=20, blank=True)
    
    # Contact
    contact_email = models.EmailField('البريد الإلكتروني', blank=True)
    contact_phone = models.CharField('رقم الهاتف', max_length=20, blank=True)
    
    # Pages Content
    about_text = models.TextField('من نحن بالعربي', blank=True)
    about_text_en = models.TextField('من نحن بالإنجليزي', blank=True)
    privacy_policy = models.TextField('سياسة الخصوصية بالعربي', blank=True)
    privacy_policy_en = models.TextField('سياسة الخصوصية بالإنجليزي', blank=True)
    terms_conditions = models.TextField('الشروط والأحكام بالعربي', blank=True)
    terms_conditions_en = models.TextField('الشروط والأحكام بالإنجليزي', blank=True)
    
    # Display Settings
    coupons_per_page = models.PositiveIntegerField('عدد الكوبونات في الصفحة', default=12)
    stores_per_page = models.PositiveIntegerField('عدد المتاجر في الصفحة', default=16)
    
    # Features
    enable_registration = models.BooleanField('تفعيل التسجيل', default=True)
    enable_favorites = models.BooleanField('تفعيل المفضلة', default=True)
    enable_notifications = models.BooleanField('تفعيل الإشعارات', default=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField('وضع الصيانة', default=False)
    maintenance_message = models.TextField('رسالة الصيانة', blank=True, default='الموقع تحت الصيانة، سنعود قريباً')
    
    # App Store Links
    play_store_url = models.URLField('رابط Google Play', blank=True)
    app_store_url = models.URLField('رابط App Store', blank=True)

    class Meta:
        verbose_name = 'إعدادات التطبيق'
        verbose_name_plural = 'إعدادات التطبيق'

    def __str__(self):
        return self.app_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_app_name(self, lang='ar'):
        if lang == 'en' and self.app_name_en:
            return self.app_name_en
        return self.app_name


class CouponUsage(models.Model):
    ACTION_CHOICES = [
        ('view', 'مشاهدة'),
        ('copy', 'نسخ'),
        ('click', 'نقر'),
    ]
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usage_logs', verbose_name='الكوبون')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='المستخدم')
    action = models.CharField('الإجراء', max_length=20, choices=ACTION_CHOICES, default='copy')
    ip_address = models.GenericIPAddressField('عنوان IP', null=True, blank=True)
    user_agent = models.TextField('معلومات المتصفح', blank=True)
    device_type = models.CharField('نوع الجهاز', max_length=20, blank=True)
    created_at = models.DateTimeField('التاريخ', auto_now_add=True)

    class Meta:
        verbose_name = 'سجل استخدام'
        verbose_name_plural = 'سجلات الاستخدام'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.coupon.code} - {self.action}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='المستخدم')
    phone = models.CharField('رقم الهاتف', max_length=20, blank=True)
    avatar = models.ImageField('الصورة الشخصية', upload_to='avatars/', blank=True, null=True)
    preferred_language = models.CharField('اللغة المفضلة', max_length=2, choices=[('ar', 'العربية'), ('en', 'English')], default='ar')
    receive_notifications = models.BooleanField('استلام الإشعارات', default=True)
    receive_emails = models.BooleanField('استلام البريد', default=True)
    is_banned = models.BooleanField('محظور', default=False)
    ban_reason = models.TextField('سبب الحظر', blank=True)
    created_at = models.DateTimeField('تاريخ التسجيل', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        verbose_name = 'ملف مستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class ContactMessage(models.Model):
    name = models.CharField('الاسم', max_length=100)
    email = models.EmailField('البريد الإلكتروني')
    phone = models.CharField('الهاتف', max_length=20, blank=True)
    subject = models.CharField('الموضوع', max_length=200)
    message = models.TextField('الرسالة')
    is_read = models.BooleanField('مقروءة', default=False)
    is_replied = models.BooleanField('تم الرد', default=False)
    reply_message = models.TextField('الرد', blank=True)
    replied_at = models.DateTimeField('تاريخ الرد', null=True, blank=True)
    created_at = models.DateTimeField('تاريخ الإرسال', auto_now_add=True)

    class Meta:
        verbose_name = 'رسالة تواصل'
        verbose_name_plural = 'رسائل التواصل'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"