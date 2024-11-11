from django.shortcuts import render,get_object_or_404,redirect
from .models import Article
from category .models import Category
from django.db.models import Q
from .forms import CommentForm
from .models import Comment
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms import SubscriptionForm
# additional imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

# Create your views here.
def index(request,categories=None,):
    # # Get the current date and format it
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            
            form.save()
            messages.success(request, 'Thank you for subscribing!')
            return redirect('index')  # Change to your desired redirect
    else:
        form = SubscriptionForm()  # Instantiate an empty form for GET requests

    # current_date = datetime.now().strftime("%A, %B %d, %Y")
    articles = Article.objects.select_related('category').order_by('-published_date').all()  # Fetch articles with related categories
    categories = Category.objects.all()
    # Fetch the latest articles, for example, the latest 5 articles
    latest_articles = Article.objects.order_by('-published_date')[:6]
     # Fetch top 5 articles ordered by views
    trending_articles = Article.get_trending_articles(limit=5)  # Limit to top 5 articles
   
    return render(request, 'blog/index.html',{'articles':articles,
                                              'categories':categories,
                                              'trending_articles':trending_articles,
                                              'latest_articles':latest_articles,
                                              'form':form
                                              })

def trending_news(request):
    
    return render(request, 'trending_news.html',{}) 


from django.db.models import Count

def NewsStore(request, category_slug=None):
    category = None
    articles = None
    categories = Category.objects.all()
    page_number = request.GET.get('page', 1)  # Default to page 1 if not provided

    # Filter articles by category if a category slug is provided
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        articles = Article.objects.filter(category=category)  # Filter articles by category
    else:
        articles = Article.objects.all()  # Get all articles

    # Annotate articles with the count of top-level comments
    articles = articles.annotate(top_comment_count=Count('comments', filter=Q(comments__parent=None)))

    # Create paginator object with the filtered articles
    paginator = Paginator(articles, 2)  # Show 2 articles per page
    articles_page = paginator.get_page(page_number)  # Get the articles for the current page

    # Fetch top-level comments related to the articles on the current page
    comments = {}
    for article in articles_page:
        comments = Comment.objects.filter(article=article, parent=None).order_by('-created_date').filter().count()

    # Count total articles
    count = articles.count()

    # Render the main page with all necessary context
    return render(request, 'blog/news_store.html', {
        'articles': articles_page,  # Pass paginated articles to the template
        'category': category,
        'count': count,
        'categories': categories,
        'comments': comments,
    })
    
def article_list(request):
    categories = Category.objects.all()
    page_number = request.GET.get('page', 1)  # Default to page 1 if not provided
    all_articles = Article.objects.all()  # Get all articles

    # Create paginator object with all articles
    paginator = Paginator(all_articles, 6)  # Show 6 articles per page
    articles_page = paginator.get_page(page_number)  # Get the articles for the current page

    return render(request, 'blog/news_store.html', {
        'articles': articles_page,  # Pass paginated articles to the template
        'total_count': all_articles.count(),
        'categories':categories # Total count of all articles
    })
    
    
def Article_detail(request, category_slug, article_slug):
    categories = Category.objects.all()
    
    # Get the article using category_slug and article_slug
    article = get_object_or_404(Article, category__slug=category_slug, slug=article_slug)
    
    # Increment views count
    article.increment_views()
    
    # Fetch trending articles
    trending_articles = Article.objects.exclude(id=article.id).order_by('-published_date')[:8]
    old_article_news = Article.objects.exclude(id=article.id).order_by('published_date')[:8]
    
    # Fetch top-level comments related to the article
    comments = Comment.objects.filter(article=article, parent=None).order_by('-created_date')
    
    # Prepare replies for each top-level comment
    for comment in comments:
        comment.replies_list = Comment.objects.filter(parent=comment).order_by('-created_date')
    
    comment_form = CommentForm()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.article = article
            
            parent_id = request.POST.get('parent')  # Get the parent ID from the form
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                # Check if the user is trying to reply to their own comment
                if parent_comment.user == request.user:
                    messages.error(request, "You cannot reply to your own comment.")
                    return redirect('article_detail', category_slug=category_slug, article_slug=article_slug)
                comment.parent_id = parent_id
            
            comment.save()
            messages.success(request, "Comment has been posted.")
            return redirect('article_detail', category_slug=category_slug, article_slug=article_slug)

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'trending_articles': trending_articles,
        'categories': categories,
        'old_article_news': old_article_news,
        'comment_form': comment_form,
        'comments': comments,  # Include only top-level comments
        'category_slug': category_slug,
        'article_slug': article_slug, 
    })
# Additional function for TinyMCE
@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES:
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)  # Save the file
        file_url = fs.url(filename)  # Get the URL of the saved file
        return JsonResponse({'location': file_url})  # Respond with the URL
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def reply_to_comment(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)

    if parent_comment.user == request.user:
                    messages.error(request, "You cannot reply to your own comment.")
    # Check if the user has already replied to this comment
    if parent_comment.replies.filter(user=request.user).exists():
        messages.error(request, "You have already replied to this comment.")
        # Construct the redirect URL using category_slug and article_slug
        category_slug = parent_comment.article.category.slug
        article_slug = parent_comment.article.slug
        
        return redirect('article_detail', category_slug=category_slug, article_slug=article_slug)

    if request.method == 'POST':
        message = request.POST.get('message')
        
        # Create the reply
        Comment.objects.create(
            article=parent_comment.article,
            user=request.user,
            message=message,
            parent=parent_comment
        )

        messages.success(request, "Your reply has been posted.")
        # Construct the redirect URL again
        category_slug = parent_comment.article.category.slug
        article_slug = parent_comment.article.slug
        
        return redirect('article_detail', category_slug=category_slug, article_slug=article_slug)

    # If the method is not POST, redirect back
    category_slug = parent_comment.article.category.slug
    article_slug = parent_comment.article.slug
    return redirect('article_detail', category_slug=category_slug, article_slug=article_slug)



# Subcribe section 


def subscribe(request):
    pass
    return render(request, 'blog/subscrib.html',)

def send_welcome_email(email):
    subject = 'Welcome to Our Newsletter!'
    message = 'Thank you for subscribing to our newsletter. We are excited to have you!'
    from_email = 'your_email@gmail.com'  # Use the same email as in settings

    send_mail(subject, message, from_email, [email])