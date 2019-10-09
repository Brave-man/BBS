from blog import models
from django import template
from django.db.models import Count


# 实例必须叫这个名字
register = template.Library()


@register.inclusion_tag(filename='left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog_obj = user_obj.blog  # 用户对应的博客

    category_list = models.Category.objects.filter(blog=blog_obj)
    tag_list = models.Tag.objects.filter(blog=blog_obj)

    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"}
    ).values('y_m').annotate(c=Count('id')).values('y_m', 'c')

    return {
        'username': username,
        'category_list': category_list,
        'tag_list': tag_list,
        'archive_list': archive_list,
    }
