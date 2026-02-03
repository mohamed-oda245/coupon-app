from django.core.management.base import BaseCommand
from core.models import Category, Store, Coupon, SliderItem, AppSettings


class Command(BaseCommand):
    help = 'Setup sample data for the coupon app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create App Settings
        settings, created = AppSettings.objects.get_or_create(pk=1)
        settings.app_name = 'كوبونات'
        settings.app_name_en = 'Coupons'
        settings.app_description = 'أفضل كوبونات الخصم والعروض من المتاجر المفضلة لديك'
        settings.app_description_en = 'Best discount coupons and offers from your favorite stores'
        settings.about_text = '''
        مرحباً بكم في موقع كوبونات!
        
        نحن منصة متخصصة في جمع أفضل كوبونات الخصم والعروض من أشهر المتاجر الإلكترونية.
        
        هدفنا هو مساعدتك في التوفير عند التسوق أونلاين من خلال توفير أحدث الأكواد والعروض الحصرية.
        
        نقوم بتحديث الكوبونات يومياً للتأكد من صلاحيتها وفعاليتها.
        '''
        settings.about_text_en = '''
        Welcome to Coupons!
        
        We are a platform specialized in collecting the best discount coupons and offers from the most famous online stores.
        
        Our goal is to help you save when shopping online by providing the latest exclusive codes and offers.
        
        We update coupons daily to ensure their validity and effectiveness.
        '''
        settings.privacy_policy = 'سياسة الخصوصية: نحن نحترم خصوصيتك ونحمي بياناتك الشخصية.'
        settings.privacy_policy_en = 'Privacy Policy: We respect your privacy and protect your personal data.'
        settings.terms_conditions = 'الشروط والأحكام: باستخدام هذا الموقع، فإنك توافق على شروطنا.'
        settings.terms_conditions_en = 'Terms: By using this site, you agree to our terms.'
        settings.contact_email = 'info@coupons.com'
        settings.save()
        self.stdout.write(self.style.SUCCESS('✓ App Settings created'))
        
        # Create Categories
        categories_data = [
            {'name': 'إلكترونيات', 'name_en': 'Electronics', 'slug': 'electronics', 'icon': 'fas fa-laptop'},
            {'name': 'أزياء', 'name_en': 'Fashion', 'slug': 'fashion', 'icon': 'fas fa-tshirt'},
            {'name': 'جمال وعناية', 'name_en': 'Beauty', 'slug': 'beauty', 'icon': 'fas fa-spa'},
            {'name': 'طعام ومطاعم', 'name_en': 'Food', 'slug': 'food', 'icon': 'fas fa-utensils'},
            {'name': 'سفر وسياحة', 'name_en': 'Travel', 'slug': 'travel', 'icon': 'fas fa-plane'},
            {'name': 'منزل وحديقة', 'name_en': 'Home', 'slug': 'home', 'icon': 'fas fa-home'},
        ]
        
        for i, cat_data in enumerate(categories_data):
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'name_en': cat_data['name_en'],
                    'icon': cat_data['icon'],
                    'order': i,
                    'is_active': True
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Categories created'))
        
        # Create Stores
        stores_data = [
            {'name': 'نون', 'name_en': 'Noon', 'slug': 'noon', 'url': 'https://www.noon.com', 'is_featured': True, 'description': 'أكبر متجر إلكتروني في الشرق الأوسط'},
            {'name': 'أمازون', 'name_en': 'Amazon', 'slug': 'amazon', 'url': 'https://www.amazon.sa', 'is_featured': True, 'description': 'تسوق ملايين المنتجات'},
            {'name': 'شي إن', 'name_en': 'SHEIN', 'slug': 'shein', 'url': 'https://www.shein.com', 'is_featured': True, 'description': 'أحدث صيحات الموضة'},
            {'name': 'نمشي', 'name_en': 'Namshi', 'slug': 'namshi', 'url': 'https://www.namshi.com', 'is_featured': True, 'description': 'أفضل الماركات العالمية'},
            {'name': 'إكسترا', 'name_en': 'Extra', 'slug': 'extra', 'url': 'https://www.extra.com', 'is_featured': False, 'description': 'إلكترونيات وأجهزة منزلية'},
            {'name': 'جرير', 'name_en': 'Jarir', 'slug': 'jarir', 'url': 'https://www.jarir.com', 'is_featured': False, 'description': 'كتب وإلكترونيات ومستلزمات مكتبية'},
            {'name': 'باث اند بودي', 'name_en': 'Bath & Body Works', 'slug': 'bath-body', 'url': 'https://www.bathandbodyworks.com.sa', 'is_featured': False, 'description': 'منتجات العناية بالجسم'},
            {'name': 'سيفورا', 'name_en': 'Sephora', 'slug': 'sephora', 'url': 'https://www.sephora.sa', 'is_featured': False, 'description': 'مستحضرات التجميل'},
        ]
        
        for i, store_data in enumerate(stores_data):
            store, created = Store.objects.get_or_create(
                slug=store_data['slug'],
                defaults={
                    'name': store_data['name'],
                    'name_en': store_data['name_en'],
                    'url': store_data['url'],
                    'description': store_data['description'],
                    'description_en': store_data['description'],
                    'is_featured': store_data['is_featured'],
                    'is_active': True,
                    'order': i
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Stores created'))
        
        # Create Coupons
        noon = Store.objects.get(slug='noon')
        amazon = Store.objects.get(slug='amazon')
        shein = Store.objects.get(slug='shein')
        namshi = Store.objects.get(slug='namshi')
        
        electronics = Category.objects.get(slug='electronics')
        fashion = Category.objects.get(slug='fashion')
        beauty = Category.objects.get(slug='beauty')
        
        coupons_data = [
            {'store': noon, 'category': electronics, 'title': 'خصم 15% على الإلكترونيات', 'title_en': '15% OFF Electronics', 'code': 'NOON15', 'discount': 15, 'is_best': True, 'is_most_used': True},
            {'store': noon, 'category': fashion, 'title': 'خصم 20% على الأزياء', 'title_en': '20% OFF Fashion', 'code': 'NOON20', 'discount': 20, 'is_best': True, 'is_most_used': False},
            {'store': noon, 'category': None, 'title': 'شحن مجاني للطلبات فوق 100 ريال', 'title_en': 'Free Shipping over 100 SAR', 'code': 'FREESHIP', 'discount': 0, 'is_best': False, 'is_most_used': True},
            {'store': amazon, 'category': electronics, 'title': 'خصم 10% على الهواتف', 'title_en': '10% OFF Phones', 'code': 'PHONE10', 'discount': 10, 'is_best': True, 'is_most_used': True},
            {'store': amazon, 'category': None, 'title': 'خصم 25 ريال على أول طلب', 'title_en': '25 SAR OFF First Order', 'code': 'FIRST25', 'discount': 0, 'is_best': False, 'is_most_used': False},
            {'store': shein, 'category': fashion, 'title': 'خصم 20% على كل شيء', 'title_en': '20% OFF Everything', 'code': 'SHEIN20', 'discount': 20, 'is_best': True, 'is_most_used': True},
            {'store': shein, 'category': fashion, 'title': 'خصم 15% + شحن مجاني', 'title_en': '15% OFF + Free Shipping', 'code': 'SHEINVIP', 'discount': 15, 'is_best': False, 'is_most_used': True},
            {'store': namshi, 'category': fashion, 'title': 'خصم 30% على الماركات', 'title_en': '30% OFF Brands', 'code': 'BRAND30', 'discount': 30, 'is_best': True, 'is_most_used': False},
            {'store': namshi, 'category': fashion, 'title': 'خصم إضافي 10%', 'title_en': 'Extra 10% OFF', 'code': 'EXTRA10', 'discount': 10, 'is_best': False, 'is_most_used': True},
        ]
        
        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                store=coupon_data['store'],
                defaults={
                    'title': coupon_data['title'],
                    'title_en': coupon_data['title_en'],
                    'category': coupon_data['category'],
                    'discount_percentage': coupon_data['discount'],
                    'description': f"استخدم الكود {coupon_data['code']} للحصول على خصم",
                    'description_en': f"Use code {coupon_data['code']} to get discount",
                    'is_active': True,
                    'is_best_offer': coupon_data['is_best'],
                    'is_most_used': coupon_data['is_most_used'],
                    'is_verified': True,
                    'used_count': 100
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Coupons created'))
        
        # Create Slider Items
        sliders_data = [
            {'title': 'أفضل عروض نون', 'title_en': 'Best Noon Deals', 'subtitle': 'خصومات تصل إلى 70%', 'subtitle_en': 'Up to 70% OFF', 'button_text': 'تسوق الآن', 'button_text_en': 'Shop Now'},
            {'title': 'كوبونات حصرية', 'title_en': 'Exclusive Coupons', 'subtitle': 'وفر أكثر مع كوبوناتنا', 'subtitle_en': 'Save more with our coupons', 'button_text': 'اكتشف المزيد', 'button_text_en': 'Discover More'},
            {'title': 'عروض الصيف', 'title_en': 'Summer Deals', 'subtitle': 'خصومات على جميع المنتجات', 'subtitle_en': 'Discounts on all products', 'button_text': 'تصفح العروض', 'button_text_en': 'Browse Deals'},
        ]
        
        for i, slider_data in enumerate(sliders_data):
            slider, created = SliderItem.objects.get_or_create(
                title=slider_data['title'],
                defaults={
                    'title_en': slider_data['title_en'],
                    'subtitle': slider_data['subtitle'],
                    'subtitle_en': slider_data['subtitle_en'],
                    'button_text': slider_data['button_text'],
                    'button_text_en': slider_data['button_text_en'],
                    'link': 'https://example.com',
                    'order': i,
                    'is_active': True
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Slider items created'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All sample data created successfully!'))
        self.stdout.write('You can now run: python manage.py runserver')