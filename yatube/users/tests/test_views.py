from django.test import TestCase, Client
from django.urls import reverse

from ..forms import CreationForm


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_signup_page_show_correct_context(self):
        """Проверка, что response.context.get('form') это наш PostForm."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertIsInstance(response.context.get('form'), CreationForm)
