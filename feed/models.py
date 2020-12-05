import datetime
import logging
import uuid
from urllib.parse import urlencode

from django.db import models

from common.models import BaseModel, CustomUser


class Source(BaseModel):
    # This is an actual feed that we poll
    user = models.ForeignKey(
        to=CustomUser,
        related_name='sources',
        on_delete=models.CASCADE,

    )
    name = models.CharField(max_length=255, blank=True, null=True)
    site_url = models.CharField(max_length=255, blank=True, null=True)
    feed_url = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField(null=True, blank=True)

    last_polled = models.DateTimeField(max_length=255, blank=True, null=True)
    due_poll = models.DateTimeField(
        default=datetime.datetime(1900, 1, 1))  # default to distant past to put new sources to front of queue
    last_modified = models.CharField(max_length=255, blank=True,
                                     null=True)  # just pass this back and forward between server and me , no need to parse

    last_result = models.CharField(max_length=255, blank=True, null=True)
    interval = models.PositiveIntegerField(default=400)
    last_success = models.DateTimeField(null=True)
    last_change = models.DateTimeField(null=True)
    live = models.BooleanField(default=True)
    status_code = models.PositiveIntegerField(default=0)
    last_302_url = models.CharField(max_length=255, null=True, blank=True)
    last_302_start = models.DateTimeField(null=True, blank=True)

    max_index = models.IntegerField(default=0)

    num_subs = models.IntegerField(default=1)

    is_cloud_flare = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name

    @property
    def best_link(self):
        if self.site_url is None or self.site_url == '':
            return self.feed_url
        else:
            return self.site_url

    @property
    def display_name(self):
        if self.name is None or self.name == "":
            return self.best_link
        else:
            return self.name


class Post(BaseModel):
    source = models.ForeignKey(
        to=Source,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.TextField(blank=True)
    body = models.TextField()
    link = models.CharField(max_length=512, blank=True, null=True)
    found = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(db_index=True)
    uuid = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    is_liked = models.BooleanField(default=None, blank=True, null=True)
    is_bookmarked = models.BooleanField(default=None, blank=True, null=True)

    def __str__(self):
        return "%s: post %s" % (self.source.display_name, self.title)

    def like(self: 'Post') -> None:
        self.is_liked = True
        return self.save()

    def unlike(self: 'Post') -> None:
        self.is_liked = False
        return self.save()


    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        if not self.created:
            self.created = datetime.datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def get_all_by_source_and_user(cls, source, user):
        return cls.objects.filter(
            source=source,
            source__user=user
        ).all()


class Proxy(BaseModel):
    address = models.CharField(max_length=255)

    def __str__(self):
        return "Proxy:{}".format(self.address)
