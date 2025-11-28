from django.urls import path 
from .views import post_list, post_detail,post_share,post_comment,post_search,like_post
from .feeds import LatestPostsFeed

app_name = 'cms_blog'
urlpatterns = [
    path('', post_list, name='post_list'),
    path('tag/<slug:tag_slug>/',post_list,name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/',post_share,name='post_share'),
    path('<int:post_id>/comment/',post_comment,name='post_comment'),
    path('feed/',LatestPostsFeed(),name='post_feed'),
    path('search/',post_search,name='post_search'),
  path('like/<int:post_id>/', like_post, name='like_post'),

    
]
