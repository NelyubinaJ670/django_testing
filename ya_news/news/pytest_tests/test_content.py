import pytest

from datetime import date

from django.conf import settings
from django.urls import reverse
from django.utils import timezone


@pytest.mark.parametrize(
    'username, access',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    ),
)
@pytest.mark.django_db
def test_user_form_access(username, access, pk_for_args):
    """Форма комментария доступна только авторизованному."""
    url = reverse('news:detail', args=pk_for_args)
    response = username.get(url)
    result = 'form' in response.context
    assert result == access


@pytest.mark.usefixtures('add_news')
@pytest.mark.django_db
def test_news_count(client):
    """ На главной странице не более 10 новостей и отсортированы """
    response = client.get(reverse('news:home'))
    object_list = list(response.context['object_list'])
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE
    assert isinstance(object_list[0].date, date)
    assert object_list == sorted(
        object_list, key=lambda news: news.date, reverse=True
    )


@pytest.mark.usefixtures('add_comments')
@pytest.mark.django_db
def test_comments_order(client, pk_for_args, news):
    """ Сортировка комментариев от свежих к старым. """
    response = client.get(reverse('news:detail', args=pk_for_args))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    assert isinstance(all_comments[0].created, timezone.datetime)
    assert all_comments == sorted(
        all_comments, key=lambda comment: comment.created)
