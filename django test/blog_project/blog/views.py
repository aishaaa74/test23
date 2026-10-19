from django.views.generic import ListView, DetailView
from .models import Blog
from django.db.models import F
from django.views.generic import ListView, DetailView
from .models import Blog


class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'
    context_object_name = 'blogs'
class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'
    context_object_name = 'blog'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)  # при несуществующем id сам даст 404
        Blog.objects.filter(pk=obj.pk).update(likes=F('likes') + 1)
        obj.refresh_from_db(fields=['likes'])
        return obj