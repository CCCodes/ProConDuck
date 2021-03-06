"""ProConDuck URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.contrib.sitemaps.views import sitemap

from . import settings
from blog.views import ReviewSitemap, ProductSitemap

sitemaps = {
    'review': ReviewSitemap,
    'product': ProductSitemap,
}

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/blog', permanent=False)),
    url(r'^blog/', include('blog.urls'), name='blog'),
    url(r'^tittlejoy/', admin.site.urls),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'blog.views.error404'
handler500 = 'blog.views.error500'
