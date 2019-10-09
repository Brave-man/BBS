"""BBS URL Configuration

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
from django.contrib import admin
from blog import views, urls as blog_urls
from BBS import settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.Login.as_view()),
    url(r'^index/', views.Index.as_view()),
    url(r'vCode/', views.v_code),

    url(r'^register/', views.RegView.as_view()),
    url(r'^logout/', views.logout1),

    # ------- 二级路由-------------
    url(r'^blog/', include(blog_urls)),
    # 给用户上传文件 配置一个处理的路由
    url(r'^media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),

    # -------- 点赞/踩灭 -------------
    url(r'^isUpDown/$', views.is_up_down),
    # ---------- 评论 ----------------
    url(r'^comment/$', views.comment),
    url(r'^$', views.let_us_go),
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
