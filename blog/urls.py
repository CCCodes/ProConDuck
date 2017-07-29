from django.conf.urls import url, handler404
from django.conf import settings
from django.views.static import serve

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^(?P<review_id>\d+)/(?P<slug>[-\w\d]+)/$', views.detail, name='detail'),
    url(r'^contact-us/', views.contact),
    url(r'^terms-of-service/', views.tos),
]

handler404 = views.error404
