from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListViewTests(TestCase):
    """Тесты списка: 5+ вариантов."""

    def setUp(self):
        self.url = reverse('blog_list')

    # 1. Страница открывается
    def test_list_status_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # 2. Используется нужный шаблон
    def test_list_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    # 3. Контента нет — показывается заглушка
    def test_list_empty(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['blogs']), 0)
        self.assertContains(response, 'Статей пока нет')

    # 4. Контент есть — все статьи в контексте и на странице
    def test_list_with_content(self):
        Blog.objects.create(title='Первая', text='Текст 1')
        Blog.objects.create(title='Вторая', text='Текст 2')
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['blogs']), 2)
        self.assertContains(response, 'Первая')
        self.assertContains(response, 'Вторая')
        self.assertNotContains(response, 'Статей пока нет')

    # 5. Ссылки ведут на правильные адреса (id в ссылке)
    def test_list_links_contain_correct_id(self):
        blog = Blog.objects.create(title='Статья', text='Текст')
        response = self.client.get(self.url)
        self.assertContains(response, f'href="/{blog.id}/"')

    # 6. По ссылке из списка действительно можно перейти
    def test_list_link_is_followable(self):
        blog = Blog.objects.create(title='Статья', text='Текст')
        response = self.client.get(blog.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['blog'].id, blog.id)

    # 7. Порядок: новые статьи сверху
    def test_list_ordering_newest_first(self):
        old = Blog.objects.create(title='Старая', text='...')
        new = Blog.objects.create(title='Новая', text='...')
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['blogs']), [new, old])


class BlogDetailViewTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(title='Тест', text='Содержимое')
        self.url = reverse('blog_detail', kwargs={'pk': self.blog.pk})

    def test_detail_status_200(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')

    def test_detail_returns_correct_object(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['blog'].id, self.blog.id)
        self.assertContains(response, 'Содержимое')

    def test_detail_nonexistent_id_returns_404(self):
        response = self.client.get(reverse('blog_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)


class BlogLikesTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(title='Тест', text='Текст')

    # Тест 1: у нового блога лайков 0
    def test_new_blog_has_zero_likes(self):
        self.assertEqual(self.blog.likes, 0)

    # Тест 2: GET на детальную страницу увеличивает счётчик до 1
    def test_detail_view_increments_likes(self):
        url = reverse('blog_detail', kwargs={'pk': self.blog.pk})
        self.client.get(url)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes, 1)