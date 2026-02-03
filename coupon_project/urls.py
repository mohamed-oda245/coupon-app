from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Guide view
def admin_guide_view(request):
    return render(request, 'admin/guide.html')

urlpatterns = [
    # Admin URLs - MUST BE FIRST
    path('admin/', admin.site.urls),
    
    # Core App URLs
    path('', include('core.urls')),
]

# Static and Media files (always include, not just in DEBUG)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)