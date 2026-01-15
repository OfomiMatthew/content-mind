from django.db import models
from django.utils import timezone 
from django.conf import settings
from django.urls import reverse 
from taggit.managers import TaggableManager
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from hitcount.models import HitCount
from django.contrib.contenttypes.fields import GenericRelation





class PublishedManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
  class Status(models.TextChoices):
    DRAFT = 'DF', 'Draft'
    PUBLISHED = 'PB', 'Published'
  title = models.CharField(max_length=300)
  slug = models.SlugField(max_length=300,unique_for_date='publish',blank=True)
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
  body = RichTextField()
  # body = models.TextField()
  like_count = models.PositiveIntegerField(default=0)
  publish = models.DateTimeField(default=timezone.now)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  status = models.CharField(max_length=3,choices = Status,default=Status.DRAFT)
  objects = models.Manager()  # The default manager.
  published = PublishedManager()  # Custom manager for published posts.
  tags = TaggableManager()
  hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk', related_query_name='hit_count')
  
  
  class Meta:
    ordering = ['publish']
    indexes = [models.Index(fields=['-publish'])]
  
  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure uniqueness for posts published on the same date
            while Post.objects.filter(publish__date=self.publish.date(), slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
  
 
  
  def get_absolute_url(self):
      return reverse("cms_blog:post_detail", args=[self.publish.year,self.publish.month,self.publish.day,self.slug])
    
    
class Comment(models.Model):
  post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
  name = models.CharField(max_length=100)
  email = models.EmailField()
  body= models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  active = models.BooleanField(default=True)
  
  class Meta:
    ordering = ['created']
    indexes = [models.Index(fields=['created'])]
    
  
  def __str__(self):
    return f"Comment by {self.name} on {self.post}"
  
  
