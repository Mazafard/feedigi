import datetime

import binascii
import random
import string, os
import uuid
from abc import abstractmethod
import copy

import shutil
from urllib.parse import urljoin

import math
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from common import const
from feedigi import settings


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_by_pk(cls, pk):
        return cls.objects.filter(pk=pk).first()

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def first_or_create(cls, **kwargs):
        obj = cls.objects.filter(**kwargs).first()
        if not obj:
            obj = cls(**kwargs)
            obj.save()
        return obj

    def load(self, **kwargs):
        for key, value in kwargs.items():
            assert key not in self._meta.fields, \
                """The requested field %s not exists""" % str(key)
            setattr(self, key, value)
        return self


class PaginationFilterable:
    @classmethod
    @abstractmethod
    def get_filterable_fields(cls):
        return []


class PaginationSortable:
    @classmethod
    @abstractmethod
    def get_sortable_fields(cls):
        return []


class PaginationSearchable:
    @classmethod
    @abstractmethod
    def get_searchable_fields(cls):
        return []


class PageNumberPagination(object):
    FILTERABLE_KEY_MAP = {
        "filter__": "__icontains",
        "exact__": "",
        "lt__": "__lt",
        "lte__": "__lte",
        "gt__": "__gt",
        "gte__": "__gte",
    }

    def __init__(self, query_set, request, page_size=20, filterable_fields=None,
                 sortable_fields=None,
                 search_fields=None):
        """
        :param django.db.models.QuerySet query_set:
        :param rest_framework.request.Request request:
        :param int page_size:
        :param list filterable_fields:
        :param list sortable_fields:
        """

        self.filterable_fields = filterable_fields
        self.sortable_fields = sortable_fields
        self.search_fields = search_fields
        self._request = request
        self.current_page = int(request.query_params.get('page', 1)) if int(
            request.query_params.get('page', 1)) > 0 else 1
        try:
            self.page_size = int(
                self._request.query_params.get('page_size', page_size))
        except ValueError as e:
            self.page_size = page_size

        self.search_text = self._request.query_params.get('search', None)
        self.query_set = query_set
        self._update_query_set()
        self.total_count = self.query_set.count()
        self.page_count = int(math.ceil(self.total_count / self.page_size))

    def _update_query_set(self):
        if self.filterable_fields is None and issubclass(self.query_set.model,
                                                         PaginationFilterable):
            self.filterable_fields = self.query_set.model.get_filterable_fields()

        if self.sortable_fields is None and issubclass(self.query_set.model,
                                                       PaginationSortable):
            self.sortable_fields = self.query_set.model.get_sortable_fields()

        if self.search_fields is None and issubclass(self.query_set.model,
                                                     PaginationSearchable):
            self.search_fields = self.query_set.model.get_searchable_fields()

        if self.filterable_fields is None:
            self.filterable_fields = []

        if self.sortable_fields is None:
            self.sortable_fields = []

        if self.search_fields is None:
            self.search_fields = []

        for value in self._get_filter_kwargs_list():
            self.query_set = self.query_set.filter(**value)

        if self.search_text:
            or_query = None
            for field in self.search_fields:
                q = Q(**{'{}__icontains'.format(field):
                             self._get_value(field, self.search_text)}
                      )
                if or_query:
                    or_query = or_query | q
                else:
                    or_query = q
            if or_query:
                self.query_set = self.query_set.filter(or_query)

        for value in self._get_sort_list():
            self.query_set = self.query_set.order_by(value)

    def _get_filter_kwargs_list(self):
        for key, value in self._request.query_params.items():
            for k, v in self.FILTERABLE_KEY_MAP.items():
                if key.startswith(k):
                    new_key = key.replace(k, "", 1)
                    if new_key in self.filterable_fields:
                        yield {
                            "{}{}".format(new_key, v): self._get_value(new_key,
                                                                       value)
                        }

    def _get_value(self, key, value, model=None):

        meta = model._meta if model else self.query_set.model._meta
        split_ket = key.split('__', 1)
        if len(split_ket) > 1:
            model = meta.get_field(split_ket[0]).related_model
            return self._get_value(split_ket[1], value, model)

        field = meta.get_field(key)

        if value == 'null':
            return None

        if isinstance(field, (models.CharField, models.TextField)):
            return self._arabic_to_persian(str(value))

        if isinstance(field, models.BooleanField):
            if value.lower() == "false" or value == "0":
                return False
            return True

        if isinstance(field, (
                models.IntegerField, models.BigIntegerField,
                models.BigAutoField)):
            try:
                return int(value)
            except ValueError as e:
                return 0

        if isinstance(field, (models.FloatField, models.DecimalField)):
            try:
                return float(value)
            except ValueError as e:
                return 0.0

        return value

    def _arabic_to_persian(self, word):
        characters = {
            'ك': 'ک',
            'دِ': 'د',
            'بِ': 'ب',
            'زِ': 'ز',
            'ذِ': 'ذ',
            'شِ': 'ش',
            'سِ': 'س',
            'ى': 'ی',
            'ي': 'ی',
            '١': '۱',
            '٢': '۲',
            '٣': '۳',
            '٤': '۴',
            '٥': '۵',
            '٦': '۶',
            '٧': '۷',
            '٨': '۸',
            '٩': '۹',
            '٠': '۰',
        }
        for k, v in characters.items():
            word = word.replace(k, v)
        return word

    def _get_sort_list(self):
        sort_field = []

        request_sort = self._request.query_params.get('sort')
        if not request_sort:
            return sort_field

        for item in request_sort.split(","):
            if item.replace("-", "", 1).replace("+", "",
                                                1) in self.sortable_fields:
                yield item

    def get_result(self):
        return self.query_set[(
                                      self.current_page - 1) * self.page_size:self.page_size * self.current_page]

    def get_total_count(self):
        return self.total_count

    def get_last_page(self):
        return self.page_count if self.page_count > 0 else 1

    def has_next_page(self):
        return self.current_page < self.get_last_page()

    def has_prev_page(self):
        return self.current_page > 1

    def get_next_page(self):
        if self.has_next_page():
            return self.current_page + 1

    def get_prev_page(self):
        if self.has_prev_page():
            return self.current_page - 1

    def get_first_page(self):
        return 1

    def get_pagination_headers(self):
        return {
            "X-Pagination-Total-Count": self.get_total_count(),
            "X-Pagination-Page-Count": self.get_last_page(),
            "X-Pagination-Current-Page": self.current_page,
            "X-Pagination-Per-Page": self.page_size,
            "X-Pagination-Sortable-Fields": ",".join(self.sortable_fields),
            "X-Pagination-Filterable-Fields": ",".join(self.filterable_fields),
            "X-Pagination-Searchable-Fields": ",".join(self.search_fields),
            "Link": self.get_links()
        }

    def get_links(self):

        url = "{0}://{1}{2}".format(
            self._request.scheme,
            self._request.get_host(),
            self._request.path,
        )

        def get_link(data):
            query_params = copy.copy(self._request.query_params)
            query_params._mutable = True
            query_params['page'] = data['page_number']
            return "<{rout}?{query_params}>; rel={rel}".format(
                rout=url,
                query_params=query_params.urlencode(safe="/"),
                rel=data['rel']
            )

        links = [{
            "page_number": 1,
            "rel": "first",
        }]

        if self.has_prev_page():
            links.append({
                "page_number": self.get_prev_page(),
                "rel": "prev",
            })

        links.append({
            "page_number": self.current_page,
            "rel": "self",
        })

        if self.has_next_page():
            links.append({
                "page_number": self.get_next_page(),
                "rel": "next",
            })

        links.append({
            "page_number": self.get_last_page(),
            "rel": "last",
        })

        return ", ".join([get_link(link) for link in links])


##########################################################################################
# DataBase Models
##########################################################################################

class VerificationText(BaseModel):
    verification_type = models.CharField(unique=True,
                                         choices=const.VERIFICATION_TEXT_TYPE_CHOICES,
                                         max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True,
                             default=None)
    text = models.TextField()

    @classmethod
    def get_with_type(cls, verification_type):
        return cls.objects.filter(verification_type=verification_type).first()

    def __str__(self):
        return self.get_verification_type_display()


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    objects = UserManager()
    email = models.EmailField(null=True, blank=True, unique=True)
    cellphone = models.CharField(max_length=63, unique=True, null=True)

    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=255, null=True, blank=True)
    password_verification_code = models.CharField(max_length=255, null=True, blank=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @classmethod
    def create_new_user(cls, email, cellphone, password, **extra_fields):
        user = cls(
            email=email,
            cellphone=cellphone,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def get_with_cellphone(cls, cellphone):
        return cls.objects.filter(cellphone=cellphone).first()

    @classmethod
    def get_with_email(cls, email):
        return cls.objects.filter(email=email).first()

    def update_last_login(self):
        self.last_login = datetime.datetime.now()
        self.save()

    def get_new_auth_token(self):
        model = JwtToken(user=self)
        model.save()

        payload = jwt_payload_handler(self)
        payload['token'] = model.value
        token = jwt_encode_handler(payload)
        self.update_last_login()
        return token

    @classmethod
    def get_with_cellphone_or_create(cls, cellphone):
        reader = cls.get_with_cellphone(cellphone)
        if not reader:
            return cls.create_user_with_cellphone(cellphone), True
        return reader, False

    @classmethod
    def create_user_with_cellphone(cls, cellphone):
        obj = cls()
        obj.cellphone = cellphone
        obj.save()
        return obj

    def generate_email_verification_code(self):
        self.email_verification_code = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in
            range(settings.EMAIL_VERIFICATION_CODE_SIZE))
        self.save()

    def generate_forget_password_verification_code(self):
        self.password_verification_code = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in
            range(settings.EMAIL_VERIFICATION_CODE_SIZE))
        self.save()

    def logout(self, payload):
        return JwtToken.revoke(payload)

    @classmethod
    def get_with_email_verification(cls, code):
        return cls.objects.filter(email_verification_code=code).first()

    @classmethod
    def get_with_password_verification(cls, code):
        return cls.objects.filter(password_verification_code=code).first()

    def verify_email(self):
        self.is_email_verified = True
        self.email_verification_code = None
        self.password_verification_code = None
        self.save()


class JwtToken(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="tokens")
    value = models.CharField(db_index=True, max_length=255)

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    @classmethod
    def revoke(cls, payload):
        return cls.objects.filter(value=payload['token']).delete()


class Image(BaseModel):
    key = models.CharField(_('Key'), max_length=127, null=True, blank=True)
    uri = models.CharField(_('Uri'), max_length=255, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        image = kwargs.pop('image', None)
        super().__init__(*args, **kwargs)
        self.image = image

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def get_image_local_uri(self):
        if self.key is None:
            return ""
        line = str(self.id)
        folders = [line[i:i + 2] for i in range(0, len(line), 2)]

        return os.path.join(
            *folders[:len(folders) - 1] + ["{}.jpg".format(str(self.key))])

    def get_local_address(self, create_directory=True):
        local_address = os.path.join(settings.UPLOAD_DIRECTORY,
                                     self.get_image_local_uri())
        if create_directory:
            directory = os.path.dirname(local_address)
            if not os.path.exists(directory):
                os.makedirs(directory)
        return local_address

    def get_url_address(self):
        local_address = self.get_image_local_uri()
        if local_address != "":
            return urljoin(settings.CDN_DOMAIN, local_address)
        else:
            return ""

    def save(self, *args, **kwargs):
        if self.image:
            self.key = uuid.uuid4() if self.key is None else self.key
            self.uri = self.get_image_local_uri()
            super().save(*args, **kwargs)
            self.refresh_from_db()
            self._save_image()
        else:
            super().save(*args, **kwargs)

    def _save_image(self):
        with open(self.get_local_address(), str("wb")) as f:
            shutil.copyfileobj(self.image.file, f)

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.get_local_address())
        except OSError:
            pass
        return super().delete(using=using, keep_parents=keep_parents)

    @property
    def image_url(self):
        return self.get_url_address()

    def __str__(self):
        return self.get_url_address()


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name


from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
