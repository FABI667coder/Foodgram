from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'id', 'first_name', 'last_name', )
    search_fields = ('username', 'id', )
    list_filter = ('username', 'id', )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', )
    search_fields = ('id', )
    list_filter = ('id', )
