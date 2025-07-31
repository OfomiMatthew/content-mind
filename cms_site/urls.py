from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.urls import path,include
from cms_blog.sitemaps import PostSitemap

sitemaps = {
    'posts':PostSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cms_blog.urls',namespace='cms_blog')),
    path('sitemap.xml',sitemap,{'sitemaps':sitemaps},name='django.contrib.sitemaps.views.sitemap')
]
