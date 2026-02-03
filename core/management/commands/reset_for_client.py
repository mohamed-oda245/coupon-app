from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import *
import os
import shutil
from django.conf import settings


class Command(BaseCommand):
    help = 'Reset everything for client delivery'

    def handle(self, *args, **kwargs):
        self.stdout.write('🧹 Cleaning up for client...\n')
        
        # Delete all data
        models_to_clear = [
            CouponUsage, UserNotification, Notification, Favorite,
            Coupon, Store, Category, SliderItem, 
            ContactMessage, UserProfile, AppSettings
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'   Deleted {count} {model.__name__}')
        
        # Delete users
        User.objects.all().delete()
        self.stdout.write('   Deleted all users')
        
        # Clean media folders
        media_folders = ['stores', 'coupons', 'slider', 'avatars', 'settings', 'categories', 'notifications']
        for folder in media_folders:
            folder_path = os.path.join(settings.MEDIA_ROOT, folder)
            if os.path.exists(folder_path):
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        self.stdout.write('   Cleaned media folders')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Everything cleaned!'))
        self.stdout.write(self.style.SUCCESS('📦 Ready for client delivery'))
        self.stdout.write(self.style.SUCCESS('\nClient will see the initial setup page'))