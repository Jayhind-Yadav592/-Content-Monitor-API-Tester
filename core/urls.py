from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='api_tester.html')),

    # PDF Required Endpoints:
    # POST   /keywords/      → Create a keyword
    # GET    /keywords/      → List all keywords
    # POST   /scan/          → Trigger a scan
    # POST   /scan/load-mock/ → Load mock data
    # GET    /flags/         → List flags
    # PATCH  /flags/{id}/    → Update review status

    path('keywords/', include('keywords.urls')),
    path('flags/', include('flags.urls')),
    path('scan/', include('scanner.urls')),
    path('content/', include('content.urls')),
]
