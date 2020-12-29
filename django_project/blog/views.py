import sys, os

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .models import Post


def home(request):
    context = {
        'posts': Post.objects.all(),
        'users': User.objects.all(),
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user)


def superuser_required():
    def wrapper(wrapped):
        class WrappedClass(UserPassesTestMixin, wrapped):
            def test_func(self):
                return self.request.user.is_superuser

        return WrappedClass

    return wrapper

class PostDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'post': Post.objects.get(pk=kwargs.get('pk')),
        })
        return context

    def post(self, request, *args, **kwargs):
        code_part = request.POST['code_area']
        input_part = request.POST['input_area']
        original_input = input_part
        input_part = input_part.replace("\n", " ").split(" ")

        def input():
            a = input_part[0]
            del input_part[0]
            return a

        try:
            orig_stdout = sys.stdout
            sys.stdout = open(os.path.join(settings.MEDIA_ROOT, 'file.txt'), 'w')
            exec(code_part)
            sys.stdout.close()
            sys.stdout = orig_stdout
            output = open(os.path.join(settings.MEDIA_ROOT, 'file.txt'), 'r')
            output = output.read()
        except Exception as e:
            sys.stdout.close()
            sys.stdout = orig_stdout
            output = e
            #output = output.read()
        print(output)

        context = self.get_context_data(**kwargs)
        context.update({
            'posts': Post.objects.get(pk=kwargs.get('pk')),
            'code': code_part,
            'input': original_input,
            'output': output
        })

        return TemplateResponse(self.request, self.template_name, context)


@superuser_required()
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


@superuser_required()
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    # def test_func(self):
    #     if self.request.user:
    #         return True
    #     return False


@superuser_required()
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/'


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def welcome(request):
    return render(request, 'blog/welcome.html', {'title': 'Welcome'})