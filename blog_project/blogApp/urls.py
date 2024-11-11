from django.urls import path
from .import views

urlpatterns = [
    path('',views.index,name='index'),
    path('category/<slug:category_slug>/', views.NewsStore, name='store_by_category'),  # For category-specific products
    path('articles/', views.article_list, name='article_list'),  # URL for listing all articles
    path('trending/', views.trending_news, name='trending_news'),
    path('category/<slug:category_slug>/article/<slug:article_slug>/', views.Article_detail, name='article_detail'),
    path('reply/<int:comment_id>/', views.reply_to_comment, name='reply_to_comment'),
   

    # Addition path for upload images or file i admin panel in content colum
    path('tinymce/upload/', views.upload_image, name='upload_image'),
]
    
