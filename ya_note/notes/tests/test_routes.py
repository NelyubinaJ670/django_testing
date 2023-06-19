from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ Фикстуры. """
        cls.author = User.objects.create(username='Авторизованный')
        cls.reader = User.objects.create(username='НЕ авторизованный')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug'
        )

    def test_pages_availability(self):
        """ home,login,logout,signup доступны анонимному пользователям."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for page in urls:
            with self.subTest(page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authentication_notes_done_add(self):
        """ notes/, done/, add/ доступны аутентифицированному пользователю."""
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        for page in urls:
            with self.subTest(
                    user=self.client.force_login(self.author), page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_only_to_authorized(self):
        """ edit, detail, delete доступны только авторизованному."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for page in urls:
                with self.subTest(user=user, page=page):
                    url = reverse(page, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for(self):
        """ Переадресация на страницу регистрации. """
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
