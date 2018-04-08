# from django.db import models
#
# from wagtail.core.models import Page
#
#
# class HomePage(Page):
#     pass


# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.template.response import TemplateResponse

from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel
from wagtailmenus.models import MenuPage
from wagtail.core.models import Page, Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class HomePage(Page):
    """
    几何首页model
    """
    logo_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=u'首页logo',
        help_text=u'首页logo'
    )

    tel = models.CharField(max_length=255, null=True, blank=True, help_text=u'联系方式')
    panels = [
        ImageChooserPanel('logo_image'),
        FieldPanel('tel'),
    ]

    content_panels = Page.content_panels + panels

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




