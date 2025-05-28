from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Post, Like, Connection, Comment


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'slug')
    readonly_fields = ('slug', 'created_at', 'updated_at')

# Removed the first Comment registration

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content_preview', 'likes_count', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('author__username', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')
    readonly_fields = ('created_at',)


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'content_preview', 'parent', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('author__username', 'content', 'post__id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)