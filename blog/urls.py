from django.conf.urls import url

from . import views

app_name = "blog"

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^(?P<review_id>\d+)/(?P<slug>[-\w\d]+)/$', views.detail, name='detail'),
    url(r'^contact-us/$', views.contact, name='contact'),
    url(r'^contact-us/submit/$', views.contact_submit, name='contact_submit'),
    url(r'^terms-of-service/$', views.tos, name="tos"),
    url(r'^privacy-policy/$', views.privacy, name="privacy"),
    url(r'^about/$', views.about, name="about"),
    url(r'^signup/?(?P<success>[-\w\d]+)/?$', views.signup, name='signup'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^error404/$', views.error404, name='error404'),
    url(r'^category/(?P<category_name>[-\w\d]+)/$', views.category, name='category')
]
