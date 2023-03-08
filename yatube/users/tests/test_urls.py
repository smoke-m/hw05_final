from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.token = default_token_generator.make_token(cls.user)
        cls.uidb64 = urlsafe_base64_encode(force_bytes(cls.user.id))
        cls.SIGNUP = reverse('users:signup')
        cls.LOGIN = reverse('users:login')
        cls.LOGOUT = reverse('users:logout')
        cls.PASS_CHANGE = reverse('users:password_change')
        cls.PASS_CHANGE_DONE = reverse('users:password_change_done')
        cls.PASS_RESET = reverse('users:password_reset')
        cls.PASS_RESET_DONE = reverse('users:password_reset_done')
        cls.PASS_RESET_CONFIRM = reverse(
            'users:password_reset_confirm', args=(cls.uidb64, cls.token))
        cls.PASS_RESET_COMPLETE = reverse('users:password_reset_complete')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_exists_at_desired_location_for_anonymous(self):
        """Проверка доступности адрессов."""
        names = [
            (self.SIGNUP, True), (self.LOGIN, True), (self.LOGOUT, True),
            (self.PASS_RESET, True), (self.PASS_RESET_DONE, True),
            (self.PASS_RESET_CONFIRM, True), (self.PASS_RESET_COMPLETE, True),
            (self.PASS_CHANGE, False), (self.PASS_CHANGE_DONE, False),
        ]
        for address, boolean_item in names:
            with self.subTest(address=address):
                if boolean_item:
                    response = self.guest_client.get(address)
                else:
                    response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous(self):
        """перенаправление анонимного пользователя на страницу логина."""
        url_names_redirect = [
            (self.PASS_CHANGE, f'{self.LOGIN}?next={self.PASS_CHANGE}'),
            (self.PASS_CHANGE_DONE,
             f'{self.LOGIN}?next={self.PASS_CHANGE_DONE}'),
        ]
        for address, redirect in url_names_redirect:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect)

    def test_namespace_uses_correct_page(self):
        """namespace:name использует соответствующий шаблон."""
        templates_url_names = [
            ('users/signup.html', self.SIGNUP),
            ('users/login.html', self.LOGIN),
            ('users/password_change_form.html', self.PASS_CHANGE),
            ('users/password_change_done.html', self.PASS_CHANGE_DONE),
            ('users/password_reset_form.html', self.PASS_RESET),
            ('users/password_reset_done.html', self.PASS_RESET_DONE),
            ('users/password_reset_confirm.html', self.PASS_RESET_CONFIRM),
            ('users/password_reset_complete.html', self.PASS_RESET_COMPLETE),
            ('users/logged_out.html', self.LOGOUT),
        ]
        for template, address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_namespace_uses_correct_urls(self):
        """namespace:name использует соответствующий URL-адрес."""
        templates_url_names = [
            (self.SIGNUP, '/auth/signup/'),
            (self.LOGIN, '/auth/login/'),
            (self.PASS_CHANGE, '/auth/password_change/'),
            (self.PASS_CHANGE_DONE, '/auth/password_change/done/'),
            (self.PASS_RESET, '/auth/password_reset/'),
            (self.PASS_RESET_DONE, '/auth/password_reset/done/'),
            (self.PASS_RESET_CONFIRM,
                f'/auth/reset/{self.uidb64}/{self.token}/'),
            (self.PASS_RESET_COMPLETE, '/auth/reset/done/'),
            (self.LOGOUT, '/auth/logout/'),
        ]
        for address, urls in templates_url_names:
            with self.subTest(address=address):
                self.assertEqual(address, urls, 'not correct')
