from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_exists_at_desired_location_for_anonymous(self):
        """Проверка доступности адрессов для анонимного пользователя."""
        url_names = [reverse('about:author'), reverse('about:tech')]
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ('about/author.html', '/about/author/'),
            ('about/tech.html', '/about/tech/'),
        )
        for template, address in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template(self):
        """Шаблон использует соответствующий namespace:name."""
        templates_pages_names = (
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech')),
        )
        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
