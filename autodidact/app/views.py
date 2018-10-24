import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from app.forms import LoginForm
from app.models import *


def main(request):
    template = 'index.html'

    n_users = len(ForumUser.objects.all())
    n_tags = len(Tag.objects.all())
    n_posts = len(Post.objects.all())

    context = {
        'user': request.user,
        'posts': Post.objects.order_by('-id')[:6],
        'tags': Tag.objects.order_by('-id')[:6],
        'n_posts': n_posts,
        'n_tags': n_tags,
        'n_users': n_users
    }
    return render(request, template, context)


def login_user(request):
    logout(request)

    template = 'login.html'
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)

        user_id, user = stub_auth(email, password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('app:main'))
        else:
            return HttpResponse('error login')
    else:
        form = LoginForm()

    context = {
        'user': request.user,
        'form': form
    }
    return render(request, template, context)


def stub_auth(email, password):
    if email == '' or password == '':
        return None, None

    user_dict = {
        'siddhant.k16@iiits.in': {'password': 'siddhant@1234', 'id': 1},
        'prakkash.m16@iiits.in': {'password': 'prakkash@1234', 'id': 2},
        'udayraj.s16@iiits.in': {'password': 'uday@1234', 'id': 3},
    }

    if email not in user_dict.keys():
        return None, None

    if user_dict[email]['password'] != password:
        return None, None

    user_id = user_dict[email]['id']
    return user_id, get_forum_user(email, password)


def get_forum_user(email, password):
    try:
        user = User.objects.get(username=email)
    except Exception as e:
        print(e)
        user = User()
        user.username = email
        user.email = email
        user.set_password(password)
        user.save()

    try:
        ForumUser.objects.get(django_user=user)
    except Exception as e:
        print(e)
        forum_user = ForumUser()
        forum_user.django_user = user
        forum_user.save()

    user = authenticate(username=email, password=password)
    return user


@login_required
def user_profile(request):
    template = 'profile.html'
    context = {
        'user': request.user,
    }
    return render(request, template, context)


def get_posts(request):
    template = 'posts.html'
    items_per_page = 25
    page = int(request.GET.get(key='page', default=1))

    posts = Post.objects.all()
    paginator = Paginator(object_list=posts, per_page=items_per_page)

    context = {
        'user': request.user,
        'items': paginator.page(page),
    }
    return render(request, template, context)


def get_tags(request):
    template = 'tags.html'
    items_per_page = 25
    page = int(request.GET.get(key='page', default=1))

    tags = Tag.objects.order_by('use_count').order_by('id')
    paginator = Paginator(object_list=tags, per_page=items_per_page)

    context = {
        'user': request.user,
        'items': paginator.page(page),
    }
    return render(request, template, context)


def search_tags(request):
    query = request.GET.get('query')
    limit = int(request.GET.get('limit', default=-1))

    tags = Tag.objects.filter(name__icontains=query).order_by('use_count').order_by('id')
    if limit != -1:
        tags = tags[: limit]

    tags = json.loads(serializers.serialize("json", tags))

    return JsonResponse({'response': tags})


def get_users(request):
    template = 'users.html'
    items_per_page = 25
    page = int(request.GET.get(key='page', default=1))

    forumUsers = ForumUser.objects.order_by('reputation')
    paginator = Paginator(object_list=forumUsers, per_page=items_per_page)

    context = {
        'user': request.user,
        'items': paginator.page(page),
    }
    return render(request, template, context)

@login_required
def post_details(request):
    post_id = request.GET.get('id')
    # print(post_id)
    post_obj = Post.objects.get(pk=post_id)
    # print(post_obj)
    template = 'post_details.html'
    context = {
        'user': request.user,
        'post': post_obj
    }
    # print(context['post'].title)
    return render(request, template, context)

@login_required
def tag_details(request):
    tag_id = request.GET.get('id')
    tag_obj = Tag.objects.get(pk=tag_id)
    # print(tag_obj)
    template = 'tag_details.html'
    context = {
        'user': request.user,
        'tag': tag_obj
    }
    # print(context['tag'].name)
    return render(request, template, context)

@login_required
def user_details(request):
    user_id = request.GET.get('id')
    # print(user_id)
    user_obj = ForumUser.objects.get(pk=user_id)
    # print(user_obj)
    template = 'user_details.html'
    context = {
        'user': request.user,
        'user_obj': user_obj
    }
    return render(request, template, context)


@login_required
def add_tag(request):
    if request.POST:
        tag_name = request.POST.get('tag')

        cursor = connection.cursor()
        forum_user_id = ForumUser.objects.get(django_user=request.user).id

        query = 'call add_tag("%s", %d)' % (tag_name, forum_user_id)
        cursor.execute(query)

        return HttpResponseRedirect(reverse('app:main'))
    else:
        return HttpResponse('This is a get request.')


@login_required
def add_post(request):
    if request.POST:
        print(request.POST)
        title = request.POST.get('title')
        description = request.POST.get('editor1')

        cursor = connection.cursor()
        query = 'call add_post("%s","%s", %d)' % (
            title, description, ForumUser.objects.get(django_user=request.user).id)
        print(query)
        cursor.execute(query)

        return HttpResponseRedirect(reverse('app:main'))
    else:
        template = 'add_post.html'
        context = {
            'user': request.user,
        }
        return render(request, template, context)
