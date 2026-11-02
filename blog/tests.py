from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListViewTests(TestCase):

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


class BlogModelCRUDTests(TestCase):
    """
    Полный набор CRUD-тестов для модели Blog.

    Отдельных веб-страниц (views) для создания, изменения и удаления статей
    в проекте нет — эти операции доступны только через ORM Django
    (Blog.objects.create/save/delete), поэтому они и проверяются напрямую
    на уровне модели, а не через HTTP-запросы.
    """

    # ---------- CREATE ----------

    def test_create_blog_saves_given_fields(self):
        blog = Blog.objects.create(title='Заголовок', text='Текст статьи')
        self.assertEqual(blog.title, 'Заголовок')
        self.assertEqual(blog.text, 'Текст статьи')

    def test_create_blog_default_likes_is_zero(self):
        blog = Blog.objects.create(title='Заголовок', text='Текст')
        self.assertEqual(blog.likes, 0)

    def test_create_blog_sets_created_at_automatically(self):
        blog = Blog.objects.create(title='Заголовок', text='Текст')
        self.assertIsNotNone(blog.created_at)

    def test_create_increases_total_count(self):
        count_before = Blog.objects.count()
        Blog.objects.create(title='Новая статья', text='Текст')
        self.assertEqual(Blog.objects.count(), count_before + 1)

    # ---------- READ ----------

    def test_read_existing_blog_by_pk(self):
        created = Blog.objects.create(title='Статья', text='Текст')
        fetched = Blog.objects.get(pk=created.pk)
        self.assertEqual(fetched.title, 'Статья')
        self.assertEqual(fetched.text, 'Текст')

    def test_read_nonexistent_blog_raises_does_not_exist(self):
        with self.assertRaises(Blog.DoesNotExist):
            Blog.objects.get(pk=999999)

    # ---------- UPDATE ----------

    def test_update_blog_title_is_saved(self):
        blog = Blog.objects.create(title='Старый заголовок', text='Текст')
        blog.title = 'Новый заголовок'
        blog.save()
        blog.refresh_from_db()
        self.assertEqual(blog.title, 'Новый заголовок')

    def test_update_does_not_change_other_fields(self):
        blog = Blog.objects.create(title='Заголовок', text='Исходный текст')
        blog.title = 'Другой заголовок'
        blog.save()
        blog.refresh_from_db()
        self.assertEqual(blog.text, 'Исходный текст')

    def test_update_does_not_create_new_record(self):
        blog = Blog.objects.create(title='Заголовок', text='Текст')
        count_before = Blog.objects.count()
        blog.title = 'Изменённый заголовок'
        blog.save()
        self.assertEqual(Blog.objects.count(), count_before)

    # ---------- DELETE ----------

    def test_delete_removes_blog_from_database(self):
        blog = Blog.objects.create(title='Удаляемая статья', text='Текст')
        pk = blog.pk
        blog.delete()
        self.assertFalse(Blog.objects.filter(pk=pk).exists())

    def test_delete_decreases_total_count(self):
        blog = Blog.objects.create(title='Удаляемая статья', text='Текст')
        count_before = Blog.objects.count()
        blog.delete()
        self.assertEqual(Blog.objects.count(), count_before - 1)

    def test_delete_does_not_affect_other_blogs(self):
        kept = Blog.objects.create(title='Остаётся', text='Текст')
        removed = Blog.objects.create(title='Удаляется', text='Текст')
        removed.delete()
        self.assertTrue(Blog.objects.filter(pk=kept.pk).exists())