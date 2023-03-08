from django.test import TestCase
from django.conf import settings

from ..models import Group, Post, Comment, Follow, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для теста',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент для теста',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str_names = [
            (str(self.group), self.group.title),
            (str(self.post), self.post.text[:settings.NUMBER_CHARACTERS]),
            (str(self.follow), f'Подписчик {self.user}, Автор {self.author}'),
            (str(self.comment), self.comment.text[:settings.NUMBER_CHARACTERS])
        ]
        for str_res, names in str_names:
            with self.subTest(str_res=str_res):
                self.assertEqual(str_res, names)
