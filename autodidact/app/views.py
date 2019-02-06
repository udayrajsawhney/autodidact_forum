import json

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core import serializers
from django.shortcuts import render
from django.db import connection
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

        user = auth(email, password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('app:main'))
        else:
            return HttpResponseRedirect(reverse('app:login'))
    else:
        form = LoginForm()

    context = {
        'user': request.user,
        'form': form
    }
    return render(request, template, context)


def auth(email, password):
    if email == '' or password == '':
        return None

    act_password = 'iamstudent'

    if password != act_password:
        return None

    return get_forum_user(email, password)


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

    sql_query = 'call autodidact_forum.search_post("%s")' % ''
    posts = list(Post.objects.raw(sql_query))

    query = request.GET.get('query')
    if query is not None:
        # posts = posts.filter(title__icontains=query)
        sql_query = 'call autodidact_forum.search_post("%s")' % query
        posts = list(Post.objects.raw(sql_query))

    paginator = Paginator(object_list=posts, per_page=items_per_page)

    context = {
        'user': request.user,
        'query': query,
        'items': paginator.page(page),
    }
    return render(request, template, context)


def get_tags(request):
    template = 'tags.html'
    items_per_page = 25
    page = int(request.GET.get(key='page', default=1))

    sql_query = 'call autodidact_forum.search_tag("%s")' % ''
    tags = list(Tag.objects.raw(sql_query))

    query = request.GET.get('query')
    if query is not None:
        # tags = tags.filter(name__icontains=query)
        sql_query = 'call autodidact_forum.search_tag("%s")' % query
        tags = list(Tag.objects.raw(sql_query))

    paginator = Paginator(object_list=tags, per_page=items_per_page)

    context = {
        'user': request.user,
        'query': query,
        'items': paginator.page(page),
    }
    return render(request, template, context)


def get_users(request):
    template = 'users.html'
    items_per_page = 25
    page = int(request.GET.get(key='page', default=1))

    sql_query = 'call autodidact_forum.search_forum_user("%s")' % ''
    forumUsers = list(ForumUser.objects.raw(sql_query))

    query = request.GET.get('query')
    if query is not None:
        # forumUsers = forumUsers.filter(django_user__email__icontains=query)
        sql_query = 'call autodidact_forum.search_forum_user("%s")' % query
        forumUsers = list(ForumUser.objects.raw(sql_query))
        print(forumUsers)

    paginator = Paginator(object_list=forumUsers, per_page=items_per_page)

    context = {
        'user': request.user,
        'query': query,
        'items': paginator.page(page),
    }
    return render(request, template, context)


@login_required
def get_profile(request):
    forumUser = ForumUser.objects.get(django_user=request.user)
    template = 'user_profile.html'
    tags = Tag.objects.filter(created_by=forumUser)[:3]
    # forumUser.tag_set.all()
    context = {
        'user': request.user,
        'user_obj': forumUser,
        'tags': tags
    }
    return render(request, template, context)


def post_details(request, pk):
    post = Post.objects.get(pk=pk)

    if request.user.is_authenticated():
        forum_user = ForumUser.objects.get(django_user=request.user)
        post.viewers.add(forum_user)
        post.save()

    template = 'post_details.html'
    context = {
        'user': request.user,
        'post': post
    }
    return render(request, template, context)


def tag_details(request, pk):
    tag = Tag.objects.get(pk=pk)
    template = 'tag_details.html'
    context = {
        'user': request.user,
        'tag': tag
    }
    return render(request, template, context)


def user_details(request, pk):
    user = ForumUser.objects.get(pk=pk)
    template = 'user_details.html'
    tags = Tag.objects.filter(created_by_id=pk)[:3]
    # user.tag_set.all()
    # print(tags)
    context = {
        'user': request.user,
        'user_obj': user,
        'tags': tags
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
        title = request.POST.get('title')
        tags = request.POST.get('tags')
        description = request.POST.get('description')

        post = Post()
        post.title = title
        post.description = description
        post.created_by = ForumUser.objects.get(django_user=request.user)
        post.save()

        tags = serializers.deserialize('json', tags)
        for i in tags:
            i.save()
            post.tags.add(i.object)

        post.save()

        return JsonResponse({'res': 'success'})
    else:
        template = 'add_post.html'
        context = {
            'user': request.user,
        }
        return render(request, template, context)


@login_required
def add_answer(request):
    if request.POST:
        post_id = int(request.POST.get('post_id'))
        description = request.POST.get('description')

        answer = Answer()
        answer.post_id = post_id
        answer.description = description
        answer.created_by = ForumUser.objects.get(django_user=request.user)
        answer.save()
        return JsonResponse({'res': 'success'})


@login_required
def add_comment(request):
    if request.POST:
        post_id = int(request.POST.get('post_id', default=-1))

        try:
            answer_id = int(request.POST.get('answer_id', default=-1))
        except Exception as e:
            print(e)
            answer_id = -1

        description = request.POST.get('description')

        comment = Comment()

        if answer_id is not -1:
            comment.answer_id = answer_id
        else:
            comment.post_id = post_id

        comment.description = description
        comment.created_by = ForumUser.objects.get(django_user=request.user)
        comment.save()
        return HttpResponseRedirect(reverse('app:postDetails', kwargs={'pk': post_id}))


@login_required
def update_tag(request):
    if request.POST:
        new_tag = request.POST.get('tag')
        old_tag = request.POST.get('oldtag')
        print(new_tag)
        print(old_tag)
        cursor = connection.cursor()
        query = 'call update_tag("%s", "%s")' % (new_tag, old_tag)
        cursor.execute(query)

        return HttpResponseRedirect(reverse('app:tags'))
    else:
        return HttpResponse('This is a get request.')


@login_required
def update_answer_accept(request):
    if request.POST:
        res = JsonResponse({'res': 'failed'})
        answer_id = int(request.POST.get('id'))
        answer = Answer.objects.get(pk=answer_id)
        if answer.post.created_by.django_user == request.user:
            post = answer.post
            obj = answer.created_by
            if answer.is_accepted == False :
                answer.is_accepted = True
                obj.reputation += 10
                obj.save()
                answer.save()
            else :
                answer.is_accepted = False
                obj.reputation -= 10
                obj.save()
                answer.save()
            # if post.accepted_answer is not None:
            #     obj = post.accepted_answer.created_by
            #     obj.reputation -= 10
            #     obj.save()
            #
            # if post.accepted_answer != answer:
            #     post.accepted_answer = answer
            #     obj = answer.created_by
            #     obj.reputation += 10
            #     obj.save()
            # else:
            #     post.accepted_answer = None

            # post.save()
            res = JsonResponse({'res': 'success'})
        return res


def search_tags(request):
    query = request.POST.get('query')
    limit = int(request.POST.get('limit', default=-1))

    tags = Tag.objects.filter(name__icontains=query).order_by('use_count').order_by('id')
    if limit != -1:
        tags = tags[: limit]

    tags = json.loads(serializers.serialize("json", tags))

    return JsonResponse({'response': tags})


def vote(request):
    type = int(request.POST.get('type'))
    id = int(request.POST.get('id'))
    value = int(request.POST.get('value'))

    forum_user = ForumUser.objects.get(django_user=request.user)
    if forum_user.reputation < 5:
        return JsonResponse({'result': 'failed'})

    if type == 0:
        obj = Post.objects.get(pk=id)
    else:
        obj = Answer.objects.get(pk=id)

    if value == 0:
        obj.up_voters.add(forum_user)
        obj.down_voters.remove(forum_user)
    else:
        obj.up_voters.remove(forum_user)
        obj.down_voters.add(forum_user)

    obj.save()

    return JsonResponse({'result': 'done', 'votes': len(obj.up_voters.all()) - len(obj.down_voters.all())})
