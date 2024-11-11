from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name= models.CharField(max_length=50,unique=True)
    slug= models.SlugField(max_length=50,unique=True)
    description = models.TextField(null=True,blank=True)
    cat_images = models.ImageField(upload_to='photos/category',null=True,blank=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural='Categories'
        
    def get_url(self):
        return reverse('store_by_category',args=[self.slug])  
    def __str__(self):
        return self.name