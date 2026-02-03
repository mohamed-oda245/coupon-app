from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import AppSettings


class Command(BaseCommand):
    help = 'Create default admin user and app settings'

    def handle(self, *args, **kwargs):
        # Create Admin User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@coupons.com',
                password='Admin@123456'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin user created!'))
            self.stdout.write('Username: admin')
            self.stdout.write('Password: Admin@123456')
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
        
        # Create App Settings
        settings, created = AppSettings.objects.get_or_create(pk=1)
        if created:
            settings.app_name = 'كوبونات'
            settings.app_name_en = 'Coupons'
            settings.app_description = 'أفضل كوبونات الخصم والعروض'
            settings.app_description_en = 'Best discount coupons and offers'
            settings.primary_color = '#27ae60'
            settings.secondary_color = '#2c3e50'
            settings.enable_registration = True
            settings.enable_favorites = True
            settings.enable_notifications = True
            settings.enable_english = True
            settings.save()
            self.stdout.write(self.style.SUCCESS('✅ App settings created!'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Setup complete!'))