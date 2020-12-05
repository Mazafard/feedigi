from django import forms

from common.models import Image
from common.widgets import ImageField


class BaseImageForm(forms.ModelForm):
    image = forms.FileField(widget=ImageField)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['image'].required = False
            self.fields['image'].widget.attrs['url'] = instance.get_url_address()

    def save(self, commit=True):
        self.instance.image = self.cleaned_data['image']
        return super().save(commit=commit)


class ImageForm(BaseImageForm):
    class Meta:
        model = Image
        fields = "__all__"
