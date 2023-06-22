from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        """ Фикстуры. """
        cls.user = User.objects.create(username='Пользователь')
        cls.url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.done_url = reverse('notes:success')
        cls.form_data = {'title': 'title',
                         'text': 'text',
                         'slug': 'slug'}
        cls.notes_count_control = Note.objects.count()

    def test_user_can_create_note(self):
        """ Залогиненный пользователь может создать заметку. """
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        note_count = Note.objects.count()
        self.assertGreater(note_count, self.notes_count_control)
        note = Note.objects.filter(slug=self.form_data['slug']).last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_user_cant__create_note(self):
        """ Анонимный пользователь не может создать заметку. """
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.login_url}?next={self.url}')
        note_count = Note.objects.count()
        self.assertEqual(note_count, self.notes_count_control)

    def test_not_possible_to_create_two_slug(self):
        """ Невозможно создать две заметки с одинаковым slug. """
        self.client.force_login(self.user)
        self.client.post(self.url, data=self.form_data)
        res_2 = self.client.post(self.url, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(res_2, form='form', field='slug', errors=warning)

    def test_filled_slug(self):
        """ Поле slug формируется при помощи pytils.translit.slugify. """
        self.client.force_login(self.user)
        self.form_data = {'title': 'Form title',
                          'text': 'Form text'}
        response = self.client.post(self.url, self.form_data)
        self.assertRedirects(response, self.done_url)
        note_count = Note.objects.count()
        self.assertGreater(note_count, self.notes_count_control)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.filter(slug=expected_slug).last()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

    NOTE_TITLE = 'Заголовок'
    NEW_NOTE_TITLE = 'Обновленный заголовок'
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновленный текст'

    @classmethod
    def setUpTestData(cls):
        """ Фикстуры. """
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='slug',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }
        cls.notes_count_control = Note.objects.count()

    def test_author_can_delete_note(self):
        """ Только автор может удалить свою заметку. """
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertLess(notes_count, self.notes_count_control)

    def test_user_cant_delete_note(self):
        """  Пользователь не может удалить чужую заметку. """
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count_control)

    def test_author_can_edit_note(self):
        """ Только автор может редактировать свою заметку. """
        self.author_client.post(self.edit_url, self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note(self):
        """ Пользователь не может редактировать чужую заметку. """
        response = self.reader_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
