import pytest
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return news


@pytest.fixture
def pk_for_args(news):
    return news.pk,


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def pk_for_comment(comment):
    return comment.pk,


@pytest.fixture
def add_news():
    add_news = News.objects.bulk_create(
        News(
            title=f'Заголовок новости {i}',
            text='Текст',
            date=timezone.now() - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return add_news


@pytest.fixture
def add_comments(news, author):
    for i in range(11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {i}'
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()
    return add_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }
