from django.test import TestCase

# Create your tests here.
import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BBS.settings")

    import django

    django.setup()
    from blog import models

    ret = models.ArticleUpDown.objects.filter(user__username='david')
    print(ret)
