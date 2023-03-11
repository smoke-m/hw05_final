import shutil
import tempfile

from math import ceil

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile


from ..models import Group, Post, Comment, Follow, User
from ..forms import PostForm, CommentForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='HasNoName')
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
                                       text='Тестовый тут текст',
                                       image=cls.image)
        cls.comment = Comment.objects.create(post=cls.post,
                                             author=cls.auth,
                                             text='Новый коммит')
        cls.follow = Follow.objects.create(user=cls.user,
                                           author=cls.auth)
        cls.INDEX = reverse('posts:index')
        cls.GROUP_POSTS = reverse('posts:group_posts_list',
                                  kwargs={'slug': cls.group.slug})
        cls.PROFILE = reverse('posts:profile',
                              kwargs={'username': cls.auth.username})
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})
        cls.POST_CREATE = reverse('posts:post_create')
        cls.POST_EDIT = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.id})
        cls.FOLLOW_INDEX = reverse('posts:follow_index')
        cls.POSTS = 28

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_auth = Client()
        self.authorized_auth.force_login(self.auth)

    def _test_right_context(self, post):
        value_expected = [(post.text, self.post.text),
                          (post.group, self.post.group),
                          (post.author, self.post.author),
                          (post.image, f'posts/{self.image.name}')]
        for value, expected in value_expected:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_create_edit_pages_show_correct_context(self):
        """Проверка, что response.context.get('form') это наш Form."""
        reverses_form = (
            (self.POST_CREATE, PostForm),
            (self.POST_EDIT, PostForm),
            (self.POST_DETAIL, CommentForm),
        )
        for value, form in reverses_form:
            with self.subTest(value=value):
                self.assertIsInstance(self.authorized_auth.get(
                    value).context.get('form'), form)

    def test_post_edit_page_show_correct_context(self):
        """В форму на редактирование передан нужный пост."""
        self.assertEqual(self.authorized_auth.get(
            self.POST_EDIT).context.get('form').instance, self.post)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        self._test_right_context(self.authorized_auth.get(
                                 self.POST_DETAIL).context['post'])
        response = self.authorized_auth.get(
            self.POST_DETAIL).context['comments'][0]
        value_expected = [(response.text, self.comment.text),
                          (response.post, self.comment.post),
                          (response.author, self.comment.author)]
        for value, expected in value_expected:
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_added(self):
        """При создании пост появляется в index,
           group_posts_list, profile, follow_index"""
        reverses = [self.INDEX, self.GROUP_POSTS,
                    self.PROFILE, self.FOLLOW_INDEX]
        self.authorized_auth.force_login(self.user)
        for revers in reverses:
            with self.subTest(revers=revers):
                self._test_right_context(self.authorized_auth.get(
                                         revers).context['page_obj'][0])

    def test_post_not_get_into_another_group_profile(self):
        """При создании пост не попал в группу и пользователю,
           для которых он не предназначен"""
        reverses_errors = [
            (reverse('posts:profile', kwargs={'username': self.user.username}),
             'пост есть у другого пользователя'),
            (reverse('posts:group_posts_list',
                     kwargs={'slug': self.another_group.slug}),
             'пост есть у другой группы'),
        ]
        for value, error in reverses_errors:
            with self.subTest(value=value):
                response = self.authorized_auth.get(value).context['page_obj']
                self.assertNotIn(self.post, response, error)

    def test_foll_not_into_another_user(self):
        """Новая запись не появляется в ленте тех, кто не подписан."""
        posts = self.authorized_auth.get(self.FOLLOW_INDEX).context['page_obj']
        self.assertNotIn(self.post, posts)

    def test_correct_pages_context(self):
        """Проверка количества постов первой и последней страницах."""
        Post.objects.all().delete()
        self.guest_client.force_login(self.user)
        posts_list = []
        for new_post in range(self.POSTS):
            posts_list.append(Post(text=f'Новый пост {new_post}',
                                   group=self.group,
                                   author=self.auth))
        Post.objects.bulk_create(posts_list)
        pages = (self.INDEX, self.PROFILE, self.GROUP_POSTS, self.FOLLOW_INDEX)
        COUNT_PAG = ceil(self.POSTS / settings.NUMB_POSTS)
        for page in pages:
            with self.subTest(page=page):
                first_page = self.guest_client.get(page)
                last_page = self.guest_client.get(page + f'?page={COUNT_PAG}')
                count_first_page = len(first_page.context['page_obj'])
                count_last_page = len(last_page.context['page_obj'])
                self.assertEqual(count_first_page, settings.NUMB_POSTS)
                self.assertEqual(count_last_page,
                                 self.POSTS - settings.NUMB_POSTS
                                 * (COUNT_PAG - 1))

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        posts = self.guest_client.get(self.INDEX).content
        Post.objects.all().delete()
        posts_del = self.guest_client.get(self.INDEX).content
        self.assertEqual(posts_del, posts)
        cache.clear()
        posts_clear = self.guest_client.get(self.INDEX).content
        self.assertNotEqual(posts_del, posts_clear)

    def test_added_follow_in_database(self):
        """после успешной подписки, подписка появляется в базе."""
        Follow.objects.all().delete()
        self.authorized_auth.force_login(self.user)
        response = self.authorized_auth.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.auth}))
        self.assertEqual(Follow.objects.count(), 1)
        self.assertRedirects(response, self.FOLLOW_INDEX)
        new_follow = Follow.objects.latest('user', 'author')
        filds_expected = [
            (new_follow.author, self.auth),
            (new_follow.user, self.user),
        ]
        for filds, expected in filds_expected:
            with self.subTest(filds=filds):
                self.assertEqual(filds, expected)

    def test_delete_follow_in_database(self):
        """после успешного удаления, подписка удаляется в базе."""
        self.authorized_auth.force_login(self.user)
        response = self.authorized_auth.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.auth}))
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.auth).exists())
        self.assertRedirects(response, self.FOLLOW_INDEX)
