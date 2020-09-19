from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

class HomePageTag(TaggedItemBase):
    content_object = ParentalKey('home.HomePage', on_delete=models.CASCADE, related_name='tagged_items')

class BaseArticlePageTag(TaggedItemBase):
    content_object = ParentalKey('home.BaseArticlePage', on_delete=models.CASCADE, related_name='tagged_items')

class HomePage(Page):

    # Database fields

    tags = ClusterTaggableManager(through=BaseArticlePageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('tags')
    ]

    # Parent page / subpage type rules

    subpage_types = ['CategoryPage']

    @property
    def get_tags(self):
        tags = self.tags.all()
        return tags

    def get_context(self, request):
        context = super(HomePage, self).get_context(request)

        feed = (BaseArticlePage.objects
            .live()
            .select_related('feed_image')
            .order_by('-first_published_at')
            )

        context['tops'] = feed[:3]

        return context

class CategoryPage(Page):

    # Database fields

    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "Category Page"

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('name', classname="full")
    ]

    # Parent page / subpage type rules

    parent_page_types = ['HomePage']
    subpage_types = ['BaseArticlePage']

class BaseArticlePage(Page):

    # Database fields

    boost_choices = (
        (0, 'default'),
        (1, 'standout'),
        (2, 'promote'),
        (3, 'advertise')
    )

    intro = models.TextField(
        blank = False
    )

    banner = RichTextField(
        blank = False
    )
    
    body = StreamField([
        ('text',  blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('embed', EmbedBlock()),
        ('html',  blocks.RawHTMLBlock())
    ])

    tags = ClusterTaggableManager(through=BaseArticlePageTag, blank=True)

    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete = models.RESTRICT,
        related_name = '+'
    )

    promote_boost = models.PositiveSmallIntegerField(
        choices = boost_choices,
        default = 0
    )

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('banner', classname="full"),
        StreamFieldPanel('body')
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),
        FieldPanel('promote_boost'),
        FieldPanel('tags')
    ]

    # Parent page / subpage type rules

    parent_page_types = ['CategoryPage']

    @property
    def page_id(self):
        return self.page_ptr_id

    @property
    def get_tags(self):
        tags = self.tags.all()
        return tags

    def get_context(self, request):
        context = super(BaseArticlePage, self).get_context(request)

        feed = (BaseArticlePage.objects
            .live()
            .select_related('feed_image')
            .order_by('-first_published_at')
        )

        context['tops'] = feed[:3]
        context['feed'] = feed

        return context
