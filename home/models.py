# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
from django import forms
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.db import models
from django.template.response import TemplateResponse

from wagtail.admin.edit_handlers import BaseChooserPanel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmenus.models import MenuPage


STATUS = (
    (0, u'待施工'),
    (1, u'水电改造'),
    (2, u'泥瓦工入场'),
    (3, u'木工入场'),
    (4, u'油漆工入场'),
    (5, u'安装阶段'),
    (6, u'验收阶段'),
    (7, u'圆满收工'),
)
STATUS_PRE = 0
STYLE = (
    (1, u'全包'),
    (2, u'半包'),
)
STYLE_PART = 2


class HomePage(Page):
    """
    几何首页model
    """
    class Meta(object):
        verbose_name_plural = verbose_name = u'几何装饰首页样式'

    def get_context(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = super(HomePage, self).get_context(args, kwargs)
        context["pic_content"] = PicContent.objects.all().order_by("-id")[:10]
        return context


class PicContent(Page):
    """
    几何首页活动页面
    """
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=u'活动图片',
        help_text=u'活动图片'
    )

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])

    panels = [
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
    ]

    content_panels = Page.content_panels + panels

    class Meta(object):
        verbose_name_plural = verbose_name = u'几何装饰首页活动配置页面'


class CommonContent(Page):
    """
    几何页面（文字、图片）配置，通用页面
    """
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])

    panels = [
        StreamFieldPanel('body'),
    ]

    content_panels = Page.content_panels + panels

    class Meta(object):
        verbose_name_plural = verbose_name = u'几何装饰通用配置页面'


class Author(Page):
    """
    几何设计师
    """
    position = models.CharField(max_length=20, help_text=u'职位', default=u'主案设计师')
    name = models.CharField(max_length=20, help_text=u'姓名')
    working_years = models.IntegerField(null=True, blank=True, help_text=u'从业年限')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=u'设计师照片',
        help_text=u'设计师照片'
    )
    profile = StreamField([('paragraph', blocks.RichTextBlock())], null=True, blank=True, help_text=u'简介')

    panels = [
        FieldPanel('position'),
        FieldPanel('name'),
        FieldPanel('working_years'),
        ImageChooserPanel('image'),
        StreamFieldPanel('profile'),
    ]
    content_panels = Page.content_panels + panels

    class Meta(object):
        """
        meta
        """
        verbose_name_plural = verbose_name = u'几何装饰设计师'

    def get_context(self, request, *args, **kwargs):
        """
        获取内容
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        slug = self.slug
        print(slug)
        context = super(Author, self).get_context(request, *args, **kwargs)
        case_objs = DecorateCase.objects.live().filter(designer__title=slug).values()
        print(case_objs)
        res_list = []
        for case in case_objs:
            li_list = BeautifulSoup(str(case["images"]), "html5lib").find_all("img")
            image_list = []
            for li in li_list:
                image_list.append(li["src"])
            case["images"] = image_list
            res_list.append(case)
        context["cases"] = res_list
        return context


class AuthorIndex(Page):
    """
    设计师列表
    """
    def get_position(self):
        """
        获取职位列表
        :return:
        """
        return set(Author.objects.live().descendant_of(self).values_list('position', flat=True))

    def get_authors(self, request):
        """
        获取设计师信息
        :return:
        """
        position = request.GET.get("position")
        author_objs = None
        if position:
            author_objs = Author.objects.filter(position__icontains=position).live().descendant_of(self).\
                order_by('last_published_at')
        else:
            author_objs = Author.objects.live().descendant_of(self).order_by('last_published_at')
        return self.paginate(request, author_objs)

    def get_context(self, request, *args, **kwargs):
        """
        获取内容
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = super(AuthorIndex, self).get_context(request)
        context["position"] = request.GET.get("position")
        context["position_list"] = list(self.get_position())
        context["authors"] = self.get_authors(request)
        context["page"] = request.GET.get("page")
        context["page_size"] = request.GET.get("page_size") if str(request.GET.get("page_size")).isdigit() else 12
        return context

    def paginate(self, request, filtered_objs, *args):
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        if not str(page_size).isdigit():
            page_size = 12
        paginator = Paginator(filtered_objs, int(page_size))

        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages

    class Meta(object):
        verbose_name_plural = verbose_name = u'几何装饰设计师列表'


class DecorateCase(Page):
    """
    装修案例
    """
    images = StreamField([('image_slider', blocks.ListBlock(ImageChooserBlock(), icon='image', label='Slider')),],
                         null=True, help_text=u'装修图片')
    designer = models.ForeignKey('home.Author', null=True, help_text=u'设计师', on_delete=models.SET_NULL)
    area = models.CharField(max_length=50, null=True, blank=True, help_text=u'区域')
    home = models.CharField(max_length=20, null=True, blank=True, help_text=u'户型')
    style = models.CharField(max_length=50, null=True, blank=True, help_text=u'风格')
    property = models.CharField(max_length=50, null=True, blank=True, help_text=u'楼盘')
    home_area = models.CharField(max_length=20, null=True, blank=True, help_text=u'面积')
    profile = StreamField([('paragraph', blocks.RichTextBlock())], null=True, blank=True, help_text=u'简介')
    status = models.IntegerField(default=STATUS_PRE, help_text=u'施工状态', choices=STATUS)
    type = models.IntegerField(default=STYLE_PART, help_text=u'方式（全包/半包）', choices=STYLE)

    panels = [
        StreamFieldPanel('images'),
        PageChooserPanel('designer'),
        FieldPanel('area'),
        FieldPanel('home'),
        FieldPanel('style'),
        FieldPanel('property'),
        FieldPanel('home_area'),
        StreamFieldPanel('profile'),
        BaseChooserPanel('status'),
        BaseChooserPanel('type'),
    ]
    content_panels = Page.content_panels + panels

    class Meta(object):
        """
        meta
        """
        verbose_name_plural = verbose_name = u'几何装修案例'

    def get_context(self, request, *args, **kwargs):
        """
        内容获取
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        slug = self.slug
        context = super(DecorateCase, self).get_context(request, *args, **kwargs)
        case_objs = DecorateCase.objects.live().filter(title=slug).values()
        print(case_objs)
        res_list = []
        for case in case_objs:
            li_list = BeautifulSoup(str(case["images"]), "html5lib").find_all("img")
            image_list = []
            for li in li_list:
                image_list.append(li["src"])
            case["images"] = image_list
            res_list.append(case)
        context["cases"] = res_list
        return context


class DecorateCaseList(Page):
    """
    装修案例列表
    """
    def get_arealist(self):
        """
        区域列表
        :return:
        """
        return list(set(DecorateCase.objects.live().descendant_of(self).values_list('area', flat=True)))

    def get_homelist(self):
        """
        户型列表
        :return:
        """
        return list(set(DecorateCase.objects.live().descendant_of(self).values_list('home', flat=True)))

    def get_stylelist(self):
        """
        风格列表
        :return:
        """
        return list(set(DecorateCase.objects.live().descendant_of(self).values_list('style', flat=True)))

    def get_cases(self, request):
        """
        获取装修案例列表
        :return:
        """

        area = request.GET.get("area", "")
        home = request.GET.get("home", "")
        style = request.GET.get("style", "")
        case_objs = DecorateCase.objects.filter(area__icontains=area, home__icontains=home, style__icontains=style).\
            live().descendant_of(self).order_by('last_published_at').values()
        res_list = []

        for case in case_objs:
            li_list = BeautifulSoup(str(case["images"]), "html5lib").find_all("img")
            image_list = []
            for li in li_list:
                image_list.append(li["src"])
            case["images"] = image_list
            res_list.append(case)
        return self.paginate(request, res_list)

    def get_context(self, request, *args, **kwargs):
        """
        获取内容
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = super(DecorateCaseList, self).get_context(request)
        context["area"] = request.GET.get("area")
        context["area_list"] = self.get_arealist()
        context["home"] = request.GET.get("home")
        context["home_list"] = self.get_homelist()
        context["style"] = request.GET.get("style")
        context["style_list"] = self.get_stylelist()
        context["cases"] = self.get_cases(request)
        context["page"] = request.GET.get("page")
        context["page_size"] = request.GET.get("page_size") if str(request.GET.get("page_size")).isdigit() else 12
        return context

    def paginate(self, request, filtered_objs, *args):
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        if not str(page_size).isdigit():
            page_size = 12
        paginator = Paginator(filtered_objs, int(page_size))

        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages

    class Meta(object):
        """
        meta
        """
        verbose_name_plural = verbose_name = u'几何装修案例列表'
