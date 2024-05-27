from django.contrib import admin
from .models import Movie, MovieTag, Tag, Cast, MovieCast, MovieWishList, Like, Comment

class MovieAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'director', 'genre', 'is_paid', 'release_date', 'ratings')
    list_filter = ['ratings', 'genre', 'is_paid']
    search_fields = ('category_name', 'vendor__vendor_name')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    ordering = ['name']

class CastAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender')
    search_fields = ['name',]
    list_filter = ('gender',)

    ordering = ('name', )

admin.site.register(Movie, MovieAdmin)
admin.site.register(Cast, CastAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(MovieTag)
admin.site.register(MovieCast)
admin.site.register(MovieWishList)
admin.site.register(Like)
admin.site.register(Comment)