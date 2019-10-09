from django.conf.urls import url
from blog import views


urlpatterns = [
    url(r'^backend/$', views.backend),
    url(r'^add_article/$', views.add_article),
    url(r'^upload/$', views.upload),
    url(r'^([\w-]+)/$', views.home),
    url(r'^([\w-]+)/(category|tag|archive)/(.*)/$', views.home),
    url(r'^([\w-]+)/article/(\d+)/$', views.article),
]


