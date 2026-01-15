from django.shortcuts import render,get_object_or_404,redirect
from .models import Post,Comment
from django.core.mail import send_mail
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.decorators.http import require_POST
from .forms import EmailPostForm,CommentForm,SearchForm,CreatePostForm
from taggit.models import Tag
from django.db.models import Count,Sum
from django.http import JsonResponse
from hitcount.models import HitCount
import json





def post_list(request,tag_slug=None):
  post_list = Post.published.all().order_by('-publish')
  liked_posts = request.session.get('liked_posts', [])
  tag = None
  if tag_slug:
    tag = get_object_or_404(Tag,slug=tag_slug)
    post_list = post_list.filter(tags__in=[tag])
  paginator = Paginator(post_list,3)
  page_number = request.GET.get('page',1)
  try:
    
    posts = paginator.page(page_number)
  except PageNotAnInteger:
    posts = paginator.page(1)
  except EmptyPage:
    posts = paginator.page(paginator.num_pages)
  return render(request,'list.html',{'posts':posts,'tag':tag,'liked_posts': liked_posts})


def post_detail(request,year,month,day,post):
  post = get_object_or_404(Post,publish__year=year,publish__month=month,publish__day=day,slug=post,status=Post.Status.PUBLISHED)
  comments = post.comments.filter(active=True)
  form = CommentForm()
  post_tags_ids = post.tags.values_list('id',flat=True)
  similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
  similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
  return render(request,'detail.html',{'post':post,'comments':comments,'form':form,'similar_posts':similar_posts})


def post_share(request,post_id):
  post = get_object_or_404(Post,id=post_id,status=Post.Status.PUBLISHED)
  sent = False
  if request.method == 'POST':
    form = EmailPostForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      post_url = request.build_absolute_uri(post.get_absolute_url())
      subject =(
        f"{cd['name']} ({cd['email']})"
        f"recommends you read {post.title}"
      )
      message = (
        f"Read {post.title} at {post_url}\n\n"
        f"{cd['name']}\'s comments: {cd['comments']}"
      )
      send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[cd["to"]]
      )
      sent=True
  else:
    form = EmailPostForm()
  return render(request,'share.html',{'post':post,'form':form,'sent':sent})  


@require_POST
def post_comment(request,post_id):
  post = get_object_or_404(Post,id=post_id,status=Post.Status.PUBLISHED)
  comment = None
  form = CommentForm(data=request.POST)
  if form.is_valid():
    comment = form.save(commit=False)
    comment.post = post
    comment.save()
  return render(request,'comment.html',{'post':post,'form':form,'comment':comment})


def post_search(request):
  form = SearchForm()
  query = None
  results = []
  if 'query' in request.GET:
    form = SearchForm(request.GET)
    if form.is_valid():
      query = form.cleaned_data['query']
      results = Post.published.filter(title__icontains=query)
  return render(request, 'search.html', {'form': form, 'query': query, 'results': results})

  


@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    liked_posts = request.session.get('liked_posts', [])

    if post_id in liked_posts:
        # Unlike
        liked_posts.remove(post_id)
        post.like_count -= 1
        post.save()
    else:
        # Like
        liked_posts.append(post_id)
        post.like_count += 1
        post.save()

    request.session['liked_posts'] = liked_posts

    return redirect(request.META.get('HTTP_REFERER', '/'))
  
  

def create_post(request):
  if request.method == 'POST':
    form = CreatePostForm(request.POST)
    if form.is_valid():
      new_post = form.save(commit=False)
      new_post.author = request.user
      new_post.slug = new_post.title.replace(' ', '-').lower()
      new_post.status = Post.Status.PUBLISHED
      new_post.save()
      form.save_m2m()
      return redirect(new_post.get_absolute_url())
  else:
    form = CreatePostForm()
  return render(request, 'create_post.html', {'form': form})




def dashboard(request):
    analytics = Post.objects.annotate(
        comments_count=Count('comments')
    ).order_by('-comments_count')

    context = {
        "analytics": analytics,
        "total_posts": Post.objects.count(),
        "total_likes": sum([post.like_count for post in analytics]),
        "total_comments": sum([post.comments_count for post in analytics]),
        "post_titles_json": json.dumps([post.title for post in analytics]),
        "likes_data_json": json.dumps([post.like_count for post in analytics]),
        "comments_data_json": json.dumps([post.comments_count for post in analytics]),
    }
    return render(request, "dashboard.html", context)
