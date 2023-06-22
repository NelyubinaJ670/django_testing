from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, pk_for_args, form_data):
    """ Анонимный пользователь не может создать комментарий. """
    comments_count_control = Comment.objects.count()
    url = reverse('news:detail', args=pk_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_control


def test_user_can_create_comment(
        author_client, author, news, form_data):
    """ Залогиненный пользователь может создать комментарий. """
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=form_data)
    new_comment = Comment.objects.get()
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() + 1
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, word):
    """ Проверка блокировки стоп-слов. """
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Текст комментария, {word}, пишем тут'}
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count


def test_author_can_delete_comment(
        author_client, pk_for_comment, pk_for_args):
    """ Только автор может удалить свой комментарий. """
    response = author_client.post(reverse('news:delete', args=pk_for_comment))
    expected_url = reverse('news:detail', args=pk_for_args) + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() - 1


def test_user_cant_delete_comment_of_another_user(
        admin_client, pk_for_comment):
    """ Пользователь не может удалить чужой комментарий. """
    comments_count_control = Comment.objects.count()
    url = reverse('news:delete', args=pk_for_comment)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_control


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment, form_data):
    """ Пользователь не может редактировать чужой комментарии. """
    url = reverse('news:edit', args=[comment.pk])
    old_comment = comment.text
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment


def test_author_can_edit_comment(
        author_client, pk_for_args, comment, form_data):
    """ Только автор может редактировать свой комментарий. """
    url = reverse('news:edit', args=[comment.pk])
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=pk_for_args) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
