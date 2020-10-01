from django.contrib import admin
from .models import Tweet
# Register your models here.

class TweetAdmin(admin.ModelAdmin):
    list_display = ["id", "content" , "user"]
    search_fields = ['user__username', 'user__email',"content__icontains"]

    class Meta:
        model = Tweet

admin.site.register(Tweet, TweetAdmin)
