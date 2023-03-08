from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersFormsPagesTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_signup_added_user_in_database(self):
        """при отправке валидной формы со страницы создания юзера
        reverse('users:signup') создаётся новаый юзер в базе данных"""
        User.objects.all().delete()
        form_data = {
            'first_name': 'Vasy',
            'last_name': 'Pupkin',
            'username': 'HasName',
            'email': 'Pupkin@yandex.ru',
            'password1': 'Hasame_1234',
            'password2': 'Hasame_1234',
        }
        response = self.guest_client.post(
            reverse('users:signup'), data=form_data, follow=True)
        self.assertRedirects(response, reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.latest('id')
        filds_expected = [
            (new_user.first_name, form_data['first_name']),
            (new_user.last_name, form_data['last_name']),
            (new_user.username, form_data['username']),
            (new_user.email, form_data['email']),
        ]
        for filds, expected in filds_expected:
            with self.subTest(filds=filds):
                self.assertEqual(filds, expected)
