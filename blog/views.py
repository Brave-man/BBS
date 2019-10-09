from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django import views
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from blog.forms import RegForm
from blog import models
from utils.mypage import MyPage
from django.db.models import Count, F
from django.db import transaction
import os
from BBS import settings
from bs4 import BeautifulSoup

# Create your views here.


def let_us_go(request):
    return render(request, 'let_us_go.html')


class Login(views.View):

    def get(self, request):
        next_url = request.GET.get('next')
        if not next_url:
            next_url = '/index/'
        return render(request, 'login.html', {'next_url': next_url})

    def post(self, request):
        res = {'code': 0}
        username = request.POST.get('username')
        password = request.POST.get('password')
        v_code = request.POST.get('v_code')

        # 首先验证验证码是否正确
        print(request.session.get('v_code', ''))
        print(v_code.upper())
        if v_code.upper() != request.session.get('v_code', ''):
            res['code'] = 1
            res['msg'] = '验证码错误'
        else:
            # 检验用户名和密码是否错误
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            else:
                res['code'] = 1
                res['msg'] = '用户名和密码错误'
        return JsonResponse(res)


class Index(views.View):
    # @method_decorator(login_required(login_url='/login/'))
    def get(self, request):
        article_list = models.Article.objects.all()

        """
        def __init__(self, page_num, all_data_amount, url_prefix, per_page_data=10, page_show_tags=9):

        :param page_num: 当前页码
        :param all_data_amount:  总的数据量
        :param url_prefix:  页码a标签的url前缀
        :param per_page_data:  每页显示多少条数据
        :param page_show_tags:  页面上显示多少个页码
        """
        page_num = request.GET.get('page', '1')
        all_data_amount = article_list.count()
        paging = MyPage(page_num, all_data_amount, url_prefix='index', per_page_data=10, page_show_tags=9)
        data = article_list[paging.start:paging.end]
        page_html = paging.ret_html()
        print(request.user)
        return render(request, 'index.html', {'article_list': data, 'page_html': page_html})


def v_code(request):
    from PIL import Image, ImageDraw, ImageFont
    import random

    # 生成一个随机颜色
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成一个图片对象
    image_obj = Image.new(
        "RGB",
        (250, 30),
        random_color()
    )

    # 画笔，望image_obj写
    draw_obj = ImageDraw.Draw(image_obj)
    # 字体, 加载本地的字体
    font_obj = ImageFont.truetype('static/font/kumo.ttf', size=28)

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        # 每次随机生成，都直接往图片上写
        draw_obj.text(
            (i*45+25, 0),  # 坐标
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj,  # 字体
        )

    # 加干扰线
    width = 250  # 图片宽度（防止越界）
    height = 35
    # for i in range(5):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=random_color())

    # 加干扰点
    for i in range(40):
        draw_obj.point([random.randint(0, width), random.randint(0, height)], fill=random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw_obj.arc((x, y, x+4, y+4), 0, 90, fill=random_color())

    v_code = "".join(tmp)  # 最终的验证码
    request.session['v_code'] = v_code.upper()  # 将验证码写入session

    # 将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, 'png')

    data = f.getvalue()  # 读取数据
    return HttpResponse(data, content_type='img/png')


class RegView(views.View):
    def get(self, request):
        form_obj = RegForm()
        return render(request, 'register.html', {'form_obj': form_obj})

    def post(self, request):
        res = {"code": 0}
        # print(request.POST)
        v_code = request.POST.get('v_code', '')

        # 首先验证验证码是否有误
        if v_code.upper() == request.session.get('v_code', ''):
            form_obj = RegForm(request.POST)
            # 使用form做校验
            if form_obj.is_valid():
                # 去除数据库不需要的数据
                form_obj.cleaned_data.pop('re_password')
                # 取到用户的头像文件
                avatar_file = request.FILES.get('avatar')
                # 数据库保存用户信息
                models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_file)
                res['msg'] = '/login/'
            else:
                res['code'] = 1
                res['msg'] = form_obj.errors
        else:
            res['code'] = 2
            res['msg'] = '验证码错误'
        return JsonResponse(res)


# 注销
def logout1(request):
    logout(request)
    return redirect('/index/')


def home(request, username, *args):
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog_obj = user_obj.blog  # 用户对应的博客

    article_list = models.Article.objects.filter(user=user_obj)  # 获取该用户的文章列表
    if args:
        if args[0] == 'category':
            article_list = article_list.filter(category__title=args[1])
        elif args[0] == 'tag':
            article_list = article_list.filter(tags__title=args[1])
        else:
            try:
                y, m = args[1].split('-')
                article_list = article_list.filter(create_time__year=y, create_time__month=m)
            except Exception as e:
                article_list = []

    page_num = request.GET.get('page', '1')
    all_data_amount = article_list.count()
    url_prefix = '{}'.format(request.path[1:-1])

    paging = MyPage(page_num, all_data_amount, url_prefix=url_prefix, per_page_data=10, page_show_tags=9)
    data = article_list[paging.start:paging.end]
    page_html = paging.ret_html()

    return render(request, 'home.html', {
        'article_list': data,
        'page_html': page_html,
        'user_obj': user_obj,
        'blog_obj': blog_obj
    })


def article(request, username, article_id):
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog_obj = user_obj.blog
    article_obj = models.Article.objects.filter(id=article_id).first()
    comment_list = models.Comment.objects.filter(article=article_obj)

    return render(request, 'article.html',
                  {
                      'article_obj': article_obj,
                      'user_obj': user_obj,
                      'blog_obj': blog_obj,
                      'comment_list': comment_list,
                  })


def is_up_down(request):
    if request.method == 'POST':
        res = {'code': 0}

        user_id = request.POST.get('user_id')
        article_id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')
        is_up = True if is_up.upper() == 'TRUE' else False
        # 不能给自己点赞
        article_obj = models.Article.objects.filter(id=article_id, user_id=user_id)
        if article_obj:
            # 表示是给自己的文章点赞
            res['code'] = 1
            res['msg'] = '不能给自己的文章点赞' if is_up else '不能反对自己的文章'
        else:
            # 3.同一个人只能给同一篇文章点赞一次
            # 4.点赞和反对两个只能选一个
            # 判断一下当前这个人和这篇文章 在点赞表里有没有记录
            is_exist = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id)

            if is_exist:
                # 表明点赞或者踩灭已经存在
                is_up = is_exist.first().is_up
                res['code'] = 1
                res['msg'] = '已经赞过该文章' if is_up else '已经反对过该文章'
            else:
                # 这里创建数据库数据与显示的点赞数保持一致，采用事务
                with transaction.atomic():
                    models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
                    if is_up:
                        models.Article.objects.filter(id=article_id).update(up_count=F('up_count')+1)
                    else:
                        models.Article.objects.filter(id=article_id).update(down_count=F('down_count') + 1)

                res['code'] = 0
                res['msg'] = '点赞成功' if is_up else '反对成功'
        return JsonResponse(res)


def comment(request):
    if request.method == 'POST':
        res = {'code': 0}
        userId = request.user.id
        articleId = request.POST.get('articleId')
        content = request.POST.get('content')
        parent_id = request.POST.get('parentId')
        print(parent_id)
        with transaction.atomic():
            # 1.创建新评论
            if parent_id:
                comment_obj = models.Comment.objects.create(user_id=userId, article_id=articleId, content=content,
                                                            parent_comment_id=parent_id)
            else:
                comment_obj = models.Comment.objects.create(user_id=userId, article_id=articleId, content=content)
            # 2.更新文章评论数
            models.Article.objects.filter(id=articleId).update(comment_count=F('comment_count')+1)

            res['data'] = {
                'id': comment_obj.id,
                'username': comment_obj.user.username,
                'content': comment_obj.content,
                'create_time': comment_obj.create_time.strftime('%Y-%m-%d %H:%M'),
            }

        return JsonResponse(res)


def backend(request):
    article_list = models.Article.objects.filter(user=request.user)
    return render(request, 'backend.html', {'article_list': article_list})


def add_article(request):
    if request.method == "POST":
        # 获取用户填写的文章内容
        title = request.POST.get("title")
        content = request.POST.get("content")
        category_id = request.POST.get("category")

        # 清洗用户发布的文章的内容，去掉script标签
        soup = BeautifulSoup(content, "html.parser")
        script_list = soup.select("script")
        for i in script_list:
            i.decompose()
        # print(soup.text)
        # print(soup.prettify())

        # 写入数据库
        with transaction.atomic():
            # 1. 先创建文章记录
            article_obj = models.Article.objects.create(
                title=title,
                desc=soup.text[0:150],
                user=request.user,
                category_id=category_id
            )
            # 2. 创建文章详情记录
            models.ArticleDetail.objects.create(
                content=soup.prettify(),
                article=article_obj
            )
        return redirect("/blog/backend/")

    # 把当前博客的文章分类查询出来
    category_list = models.Category.objects.filter(blog__userinfo=request.user)
    return render(request, "add_article.html", {"category_list": category_list})


# 富文本编辑器的图片上传
def upload(request):
    res = {"error": 0}
    print(request.FILES)
    file_obj = request.FILES.get("imgFile")
    file_path = os.path.join(settings.MEDIA_ROOT, "article_imgs", file_obj.name)
    with open(file_path, "wb") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    # url = settings.MEDIA_URL + "article_imgs/" + file_obj.name
    url = "/media/article_imgs/" + file_obj.name
    res["url"] = url
    return JsonResponse(res)
