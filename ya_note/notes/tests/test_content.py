from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ Фикстуры. """
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug'
        )

    def test_authorized_client_has_form(self):
        """ На страницы создания и редактирования заметки передаются формы. """
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        self.client.force_login(self.author)
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_object_list_in_list(self):
        """ Проверка словаря context и списка заметок."""
        notes = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, note_in_list in notes:
            self.client.force_login(user)
            with self.subTest(user=user.username, note_in_list=note_in_list):
                response = self.client.get(url)
                note_in_object_list = self.note in response.context[
                    'object_list']
                self.assertEqual(note_in_object_list, note_in_list)
