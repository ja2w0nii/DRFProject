from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from articles.serializers import ArticleSerializer
from users.models import User
from articles.models import Article
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile
from faker import Faker


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, 'png')
    return temp_file

class ArticleCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {'email': 'john@gmail.com', 'password': 'johnpassword'}
        cls.article_data = {'title': 'some title', 'content': 'some content'}
        cls.user = User.objects.create_user('john@gmail.com', 'johnpassword')

    #.client는 classmethod가 아니기 때문에 self를 사용하는 setUp 메소드 안에 넣어주어야 한다.
    def setUp(self):
        self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']

    #classmethod 사용 안 할 경우
    # def setUp(self):
    #     self.user_data = {'email': 'john@gmail.com', 'password': 'johnpassword'}
    #     self.article_data = {'title': 'some title', 'content': 'some content'}
    #     self.user = User.objects.create_user('john@gmail.com', 'johnpassword')
    #     self.access_token = self.client.post(reverse('token_obtain_pair'), self.user_data).data['access']

    def test_fail_if_not_logged_in(self):
        url = reverse("article_view")
        response = self.client.post(url, self.article_data)
        self.assertEqual(response.status_code, 401)

    def test_create_article(self):
        response = self.client.post(
            path=reverse("article_view"),
            data=self.article_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)

    def test_creat_article_with_image(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)
        self.article_data["image"] = image_file
        
        response=self.client.post(
            path=reverse("article_view"),
            data=encode_multipart(data = self.article_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)

class ArticleReadTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.articles=[]
        for i in range(10):
            cls.user = User.objects.create_user(cls.faker.email(), cls.faker.word())
            cls.articles.append(Article.objects.create(user=cls.user, title=cls.faker.sentence(), content=cls.faker.text()))

    def test_Get_article(self):
        for article in self.articles:
            url = article.get_absolute_url()
            response = self.client.get(url)
            serializer = ArticleSerializer(article).data
            for key, value in serializer.items():
                self.assertEqual(response.data[key], value)
                print(key, value)
                




