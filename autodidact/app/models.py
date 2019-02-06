from django.contrib.auth.models import User
from django.db import models


class ForumUser(models.Model):
    django_user = models.OneToOneField(User)
    reputation = models.IntegerField(default=0)

    def __str__(self):
        return str(self.django_user.username)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    use_count = models.IntegerField(default=0)
    creation_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('ForumUser')

    def __str__(self):
        return str(self.name) + ' ;' + str(self.created_by)


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    tags = models.ManyToManyField(Tag)
    #accepted_answer = models.OneToOneField('Answer', null=True, related_name='accepted_answer')
    up_voters = models.ManyToManyField('ForumUser', related_name='up_voted_post')
    down_voters = models.ManyToManyField('ForumUser', related_name='down_voted_post')
    viewers = models.ManyToManyField('ForumUser', related_name='viewed_post')
    closed = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('ForumUser', related_name='created_post')

    def __str__(self):
        return str(self.title) + ' ;' + str(self.creation_time)


class Answer(models.Model):
    description = models.CharField(max_length=1000)
    post = models.ForeignKey('Post')
    is_accepted = models.BooleanField(default=False)
    up_voters = models.ManyToManyField('ForumUser', related_name='up_voted_answer')
    down_voters = models.ManyToManyField('ForumUser', related_name='down_voted_answer')
    creation_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('ForumUser', related_name='created_answer')

    def __str__(self):
        return str(self.description)[:20] + ' ;' + str(self.creation_time)


class Comment(models.Model):
    description = models.CharField(max_length=100)
    post = models.ForeignKey('Post', null=True)
    answer = models.ForeignKey('Answer', null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('ForumUser', related_name='created_comment')

    def __str__(self):
        return str(self.description)[:20] + ' ;' + str(self.creation_time)
