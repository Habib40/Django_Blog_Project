from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
from django.db import models
from category.models import Category
from django.urls import reverse
from tinymce.models import HTMLField  # Import HTMLField from tinymce




class Author(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = HTMLField()  # Use RichTextField instead of TextField
    image = models.ImageField(upload_to='articles/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    def get_plain_content(self):
        return self.content  # This will remove all HTML tags

    def __str__(self):
        return self.title
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])
        
    @classmethod
    def get_trending_articles(cls, limit=None):
        """Get articles with views greater than 5, ordered by views descending."""
        queryset = cls.objects.filter(views__gt=5).order_by('-views')
        if limit:
            queryset = queryset[:limit]
        return queryset
    def get_url(self):
        return reverse('article_detail', args=[self.category.slug, self.slug])


class Comment(models.Model):
    article = models.ForeignKey(
        Article,  # Assuming Article is another model in your app
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        Account,  # Assuming Account is a user model in your app
        on_delete=models.CASCADE
    )
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',  # Reference to the same model
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Comment by {self.user} on {self.article}'


class Advertisement(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ads/')
    url = models.URLField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class ArticleTag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('article', 'tag')


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


