from django.contrib import admin

from django import forms
from .models import(
    Author,
    Article,
    Comment,
    Advertisement,
    Tag,
    ArticleTag,
    
    NewsletterSubscription
)

# Register your models here.

admin.site.register(Author),
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
    list_display = ['title','slug']
    class Meta:
        model = Article
        fields = '__all__'   
        
admin.site.register(Article,ArticleAdmin),




admin.site.register(Advertisement),
admin.site.register(Tag),
admin.site.register(ArticleTag),
admin.site.register(Comment),
admin.site.register(NewsletterSubscription),





    

