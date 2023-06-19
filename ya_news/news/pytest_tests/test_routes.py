from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
@pytest.mark.django_db
def test_pages_availability(client, page, args):
    """ home,detail,login,logout,signup доступны анонимному пользователю."""
    url = reverse(page, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_comment')),
        ('news:delete', pytest.lazy_fixture('pk_for_comment')),
    ),
)
def test_availability_for_comment_edit_and_delete(author_client, page, args):
    """Автор заходит на страницу комментария и удаления своего комментария."""
    url = reverse(page, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
        page, pk_for_comment, admin_client
):
    url = reverse(page, args=pk_for_comment)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_comment')),
        ('news:delete', pytest.lazy_fixture('pk_for_comment')),
    ),
)
def test_redirect_for_anonymous_client(client, page, args):
    """ Переадресация на страницу регистрации. """
    login_url = reverse('users:login')
    url = reverse(page, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
