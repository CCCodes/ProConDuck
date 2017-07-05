from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^(?P<review_id>[0-9]+)/$', views.detail, name='detail'),
]
