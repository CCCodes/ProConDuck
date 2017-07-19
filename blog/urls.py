from django.conf.urls import url, handler404

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^(?P<review_id>\d+)/(?P<slug>[-\w\d]+)/$', views.detail, name='detail'),
    url(r'^contact-us/', views.contact),
]

handler404 = views.error404
