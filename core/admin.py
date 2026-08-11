from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Entity, Banner


class BannerInlineForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'size': 24, 'class': 'banner-inline-input'}),
            'link': forms.URLInput(attrs={'size': 32, 'class': 'banner-inline-input'}),
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 30, 'class': 'banner-inline-textarea'}),
        }


class BannerInline(admin.TabularInline):
    model = Banner
    form = BannerInlineForm
    fields = ('thumbnail', 'title', 'link', 'text', 'width', 'height', 'is_active', 'created_at')
    readonly_fields = ('thumbnail', 'width', 'height', 'created_at')
    extra = 0

    def thumbnail(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="height:60px;" />', obj.image.url)
        return ''
    thumbnail.short_description = 'Image'


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'banner_count', 'is_active')
    search_fields = ('name', 'slug', 'url')
    inlines = [BannerInline]

    class Media:
        css = {
            'all': ('css/admin-inline.css',)
        }

    def banner_count(self, obj):
        return obj.banners.count()
    banner_count.short_description = 'Banners'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'entity', 'title', 'short_text', 'link', 'width', 'height', 'is_active', 'created_at')
    list_filter = ('is_active', 'entity')
    search_fields = ('title', 'text', 'link')
    list_editable = ('is_active',)
    readonly_fields = ('thumbnail', 'width', 'height', 'created_at', 'updated_at')

    def thumbnail(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="height:60px;" />', obj.image.url)
        return ''
    thumbnail.short_description = 'Image'

    def short_text(self, obj):
        if not obj.text:
            return ''
        return (obj.text[:75] + '...') if len(obj.text) > 75 else obj.text
    short_text.short_description = 'Text'
