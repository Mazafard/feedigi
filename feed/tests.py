import json

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from common.models import CustomUser, JwtToken
from feed.models import Source, Post
from feed.serializers import SourceSerializer


class SourceAPIViewTestCase(APITestCase):
    url = reverse("source_list")

    def setUp(self):
        self.credentials_user = {
            'email': 'john@snow.com',
            'password': 'you_know_nothing',
            'first_name': 'john',
            'cellphone': '09123456789',
            'last_name': 'snow',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }
        self.username = "john"
        self.email = "john@snow.com"

        self.user = CustomUser.objects.create_user(**self.credentials_user)
        self.token = self.user.get_new_auth_token()
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create(self):
        self.data_source = {
            'name': 'test1',
            'feed_url': 'test1.com/.rss',
        }

        response = self.client.post(
            path=self.url,
            data=self.data_source,
            # content_type='application/json',
        )

        self.assertEqual(201, response.status_code)

    def test_user_source(self):
        """
        Test to verify user Source list
        """
        self.data_source = {
            'name': 'test1',
            'feed_url': 'test1.com/.rss',
            'user': self.user
        }
        Source.objects.create(**self.data_source)
        response = self.client.get(self.url)
        self.assertEqual(len(json.loads(response.content)), Source.objects.count())


class SourceDetailAPIViewTestCase(APITestCase):

    def setUp(self):
        self.credentials_user = {
            'email': 'john@snow.com',
            'password': 'you_know_nothing',
            'first_name': 'john',
            'cellphone': '09123456789',
            'last_name': 'snow',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }

        self.user = CustomUser.objects.create_user(**self.credentials_user)
        self.data_update_source = {
            'name': 'test3',
            'feed_url': 'test1.com/.rss',
        }
        self.data_source = {
            'user': self.user,
            'name': 'test1',
            'feed_url': 'test1.com/.rss',
        }
        self.source = Source.objects.create(**self.data_source)
        self.url = reverse("source_detail", kwargs={"pk": self.source.pk})
        self.token = self.user.get_new_auth_token()
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_list(self):
        """
        Test to verify source object bundle
        """
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        source_serializer_data = SourceSerializer(instance=self.source).data
        response_data = json.loads(response.content)

        self.assertEqual(source_serializer_data, response_data)

    def test_update_authorization(self):
        """
            Test to verify that put call with different user token
        """
        self.credentials_hacker_user = {
            'email': 'Cersei@Lannister.com',
            'password': 'Queen_of_the_Seven_Kingdoms',
            'first_name': 'Cersei',
            'cellphone': '09123456780',
            'last_name': 'Lannister',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }

        self.hacker_user = CustomUser.objects.create_user(**self.credentials_hacker_user)
        self.hacker_token = self.hacker_user.get_new_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.hacker_token)

        # HTTP PUT
        response = self.client.put(self.url, **self.data_update_source)
        self.assertEqual(404, response.status_code)

    def test_update(self):
        response = self.client.put(self.url, self.data_update_source)
        response_data = json.loads(response.content)

        source = Source.objects.get(id=self.source.id)
        self.assertEqual(response_data.get("name"), source.name)

    #
    def test_delete_authorization(self):
        """
            Test to verify that put call with different user token
        """
        self.credentials_hacker_user = {
            'email': 'Cersei@Lannister.com',
            'password': 'Queen_of_the_Seven_Kingdoms',
            'first_name': 'Cersei',
            'cellphone': '09123456780',
            'last_name': 'Lannister',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }

        self.hacker_user = CustomUser.objects.create_user(**self.credentials_hacker_user)
        self.hacker_token = self.hacker_user.get_new_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.hacker_token)

        response = self.client.delete(self.url)
        self.assertEqual(404, response.status_code)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)


class PostAPIViewTestCase(APITestCase):

    def setUp(self):
        self.credentials_user = {
            'email': 'john@snow.com',
            'password': 'you_know_nothing',
            'first_name': 'john',
            'cellphone': '09123456789',
            'last_name': 'snow',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }

        self.user = CustomUser.objects.create_user(**self.credentials_user)
        self.data_update_post = {
            'source': self.source,
            'body': 'test122',
        }
        self.data_source = {
            'user': self.user,
            'name': 'test1',
            'feed_url': 'test1.com/.rss',
        }
        self.source = Source.objects.create(**self.data_source)

        self.url_list = reverse("post_list", kwargs={
            "pk": self.source.pk,

        })
        self.data_post = {
            'source': self.source,
            'body': 'test1',

        }
        self.post = Post.objects.create(**self.data_post)
        self.url = reverse("post_detail", kwargs={
            "pk": self.source.pk,
            "post_id": self.post.pk

        })

        self.token = self.user.get_new_auth_token()
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    # def test_create(self):
    #
    #     self.data = {
    #
    #         'body': 'test1',
    #
    #     }
    #     self.url = reverse("post_list", kwargs={
    #         "pk": self.source.pk,
    #
    #     })
    #
    #
    #     response = self.client.post(
    #         path=self.url,
    #         data=self.data,
    #         # content_type='application/json',
    #     )
    #     print(response.__dict__)
    #     self.assertEqual(201, response.status_code)

    def test_user_post(self):
        """
        Test to verify user Source list
        """

        self.data_post = {
            'body': 'test1',
            'source': self.source
        }
        Post.objects.create(**self.data_post)
        response = self.client.get(self.url_list)

        self.assertEqual(201, response.status_code)

        self.assertEqual(len(json.loads(response.content)), Post.objects.filter(source__user=self.user).count())

    def test_list(self):
        """
        Test to verify source object bundle
        """

        response = self.client.get(self.url_list)
        self.assertEqual(200, response.status_code)

        source_serializer_data = SourceSerializer(instance=self.source).data
        response_data = json.loads(response.content)

        self.assertEqual(source_serializer_data, response_data)

    def test_list_not_source_exist(self):
        """
        est to verify source object bundle
        """
        self.url_not_exist = reverse("source_detail", kwargs={"pk": self.source.pk + 1})

        response = self.client.get(self.url_not_exist)
        self.assertEqual(404, response.status_code)

    def test_update_authorization(self):
        """
            Test to verify that put call with different user token
        """
        self.credentials_hacker_user = {
            'email': 'Cersei@Lannister.com',
            'password': 'Queen_of_the_Seven_Kingdoms',
            'first_name': 'Cersei',
            'cellphone': '09123456780',
            'last_name': 'Lannister',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }

        self.hacker_user = CustomUser.objects.create_user(**self.credentials_hacker_user)
        self.hacker_token = self.hacker_user.get_new_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.hacker_token)

        # HTTP PUT
        self.url_hacked = reverse("post_detail", kwargs={
            "pk": self.source.pk,
            "post_id": self.post.pk

        })
        response = self.client.put(self.url_hacked, **self.data_update_post)
        self.assertEqual(404, response.status_code)

    def test_update(self):
        response = self.client.put(self.url, self.data_update_post)
        response_data = json.loads(response.content)

        source = Source.objects.get(id=self.source.id)
        self.assertEqual(response_data.get("name"), source.name)

    #
    def test_delete_authorization(self):
        """
            Test to verify that put call with different user token
        """
        self.credentials_hacker_user = {
            'email': 'Cersei@Lannister.com',
            'password': 'Queen_of_the_Seven_Kingdoms',
            'first_name': 'Cersei',
            'cellphone': '09123456780',
            'last_name': 'Lannister',
            'is_email_verified': True,
            'email_verification_code': '1234',
        }

        self.hacker_user = CustomUser.objects.create_user(**self.credentials_hacker_user)
        self.hacker_token = self.hacker_user.get_new_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.hacker_token)

        response = self.client.delete(self.url)
        self.assertEqual(404, response.status_code)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)

    def test_like(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)

    def test_dislike(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)
