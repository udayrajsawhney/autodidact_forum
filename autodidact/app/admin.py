from django.contrib import admin
from .models import Tag, Thread, Answer, Comment

admin.site.register(Tag)
admin.site.register(Thread)
admin.site.register(Answer)
admin.site.register(Comment)

