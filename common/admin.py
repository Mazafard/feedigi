from django.contrib import admin
from django.utils.safestring import mark_safe

from common.forms import ImageForm
from .models import *


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('key', 'image_view')
    readonly_fields = ('key', 'uri')
    form = ImageForm

    def image_view(self, obj):
        return mark_safe('<img src="{}" width=100 />'.format(obj.image_url))

    image_view.allow_tags = True


admin.site.register(CustomUser)
admin.site.register(VerificationText)
admin.site.register(JwtToken)
