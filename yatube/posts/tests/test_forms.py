import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, Comment, Follow, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test-slug')
        cls.another_group = Group.objects.create(title='Другая группа',
                                                 slug='another-slug')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.image = SimpleUploadedFile(
            'small.gif', cls.small_gif, content_type='image/gif',
        )
        cls.post = Post.objects.create(author=cls.auth,
                                       group=cls.group,
                                       text='Тестовый текст',
                                       image=cls.image)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_auth = Client()
        self.authorized_auth.force_login(self.auth)

    def test_created_from_added_page_in_database(self):
        """при отправке валидной формы со страницы создания поста
           создаётся новая запись в базе данных"""
        Post.objects.all().delete()
        new_image = SimpleUploadedFile(
            name='small_new.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': new_image,
        }
        response = self.authorized_auth.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(Post.objects.count(), 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        new_post = Post.objects.latest('pub_date')
        filds_expected = [
            (new_post.text, form_data['text']),
            (new_post.author, self.auth),
            (new_post.group.id, form_data['group']),
            (new_post.image, f'posts/{new_image.name}'),
        ]
        for filds, expected in filds_expected:
            with self.subTest(filds=filds):
                self.assertEqual(filds, expected)

    def test_edit_from_edit_page_in_database(self):
        """при отправке валидной формы со страницы редактирования поста
           происходит изменение поста с post_id в базе данных."""
        posts_count = Post.objects.count()
        another_image = SimpleUploadedFile(
            name='small_another.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Меняем текст',
            'group': self.another_group.id,
            'image': another_image,
        }
        response = self.authorized_auth.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        edit_post = Post.objects.get(id=self.post.id)
        filds_expected = [
            (edit_post.text, form_data['text']),
            (edit_post.author, self.post.author),
            (edit_post.group.id, form_data['group']),
            (edit_post.image, f'posts/{another_image.name}'),
        ]
        for filds, expected in filds_expected:
            with self.subTest(filds=filds):
                self.assertEqual(filds, expected)

    def test_added_commit_in_database(self):
        """после успешной отправки комментарий появляется в базе."""
        Comment.objects.all().delete()
        form_data = {
            'post': self.post,
            'author': self.auth,
            'text': 'Новый коммит',
        }
        response = self.authorized_auth.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        new_comment = Comment.objects.latest('created')
        filds_expected = [
            (new_comment.text, form_data['text']),
            (new_comment.author, self.auth),
            (new_comment.post, self.post),
        ]
        for filds, expected in filds_expected:
            with self.subTest(filds=filds):
                self.assertEqual(filds, expected)

    def test_added_delete_follow_in_database(self):
        """после успешной подписки(удаления),
           подписка появляется(удаляется) в базе."""
        Follow.objects.all().delete()
        form_data = {'user': self.user, 'author': self.auth}
        self.authorized_auth.force_login(self.user)
        response = self.authorized_auth.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.auth}),
            data=form_data,
            follow=True)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertRedirects(response, reverse('posts:follow_index'))
        new_follow = Follow.objects.latest('user', 'author')
        filds_expected = [
            (new_follow.author, self.auth),
            (new_follow.user, self.user),
        ]
        for filds, expected in filds_expected:
            with self.subTest(filds=filds):
                self.assertEqual(filds, expected)
        response = self.authorized_auth.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.auth}))
        self.assertEqual(Follow.objects.count(), 0)
        self.assertRedirects(response, reverse('posts:follow_index'))
