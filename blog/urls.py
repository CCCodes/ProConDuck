from django.conf.urls import url

from . import views

app_name = "blog"

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^review/(?P<review_slug>[-\w\d]+)/$', views.review,
        name='review'),
    url(r'^contact-us/$', views.contact, name='contact'),
    url(r'^contact-us/submit/$', views.contact_submit, name='contact_submit'),
    url(r'^terms-of-service/$', views.tos, name='tos'),
    url(r'^privacy-policy/$', views.privacy, name='privacy'),
    url(r'^about/$', views.about, name='about'),
    url(r'^signup/?(?P<success>[-\w\d]+)/?$', views.signup, name='signup'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^product/(?P<product_slug>[-\w\d]+)/$', views.product,
        name='product'),
    url(r'all-products/$', views.all_products, name='all_products'),
    url(r'^promotions/$', views.promotions, name='promotions')
]
