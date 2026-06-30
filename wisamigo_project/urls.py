from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/payment-dashboard/', RedirectView.as_view(url='/admin-dashboard/', permanent=False)),
    path('admin/', admin.site.urls),
    path('', include('travel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)