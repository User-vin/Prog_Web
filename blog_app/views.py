# blog/blog_app/views.py

# les données sont affichées grace aux views
# pour afficher des données il faut faire appelle à un model 
# et les affichés par l'intermédiaire d'uen view
# définie le comportement de l'application web

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.views import LogoutView
from django.db import IntegrityError
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.urls import reverse
from . import forms
from . import models

def index_view(request):
    """Retrieves all post objects from the database order by date in descending order and displays the last two in the view context,
        create a panigation and retrieves all post objects from the database order by id in descending order and displays in the view context,

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: HTTP response object that renders an HTML page template specified by the string "blog_app/index.html" with the view context.
    """
    # Récupére tous les objets Post. Récupérer les deux derniers objets Post
    # latest_posts = models.PostModels.objects.all().order_by('-date')[:2][::-1]
    most_preferred = models.PostModels.objects.annotate(num_favoris=Count('favoris')).order_by('-num_favoris')[:2]   
    
    first_post = most_preferred[0]
    second_post = most_preferred[1]
    posts = models.PostModels.objects.exclude(id__in=[first_post.id, second_post.id]).order_by('-id')[:3]
    posts2 = models.PostModels.objects.annotate(num_favoris=Count('bookmark')).exclude(id__in=[first_post.id, second_post.id]+[post.id for post in posts]).order_by('-num_favoris')[:3]
    print("most_preferred: ",most_preferred)
    print("posts: ",posts)
    print("posts2: ",posts2)
    context = {
        'first_post': first_post,
        'second_post': second_post,
        'posts': posts,
        'posts2': posts2,
    }
    # Rendre le template avec les deux derniers objets Post
    return render(request, 'blog_app/index.html', context)
    
    
def login_view(request):
    """This method is used to manage the connection of users.

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: HTTP response object that renders an HTML page template, root if the user is logged in
        else, the same page template with the view context.
    """
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)
        print(authenticate(request, username=username))
        if user is not None:
            # utilisateur trouvé dans la base de donnée
            # connectez l'utilisateur
            login(request, user)
            if request.user.is_authenticated:
                redirect_to = request.GET.get('next', '')
                print("redirect_to: ",redirect_to)
                print("request.get_full_path: ",request.get_full_path)
                return HttpResponseRedirect(redirect_to) 
        else:
            form = forms.LoginForm()
            # utilisateur non trouvé dans la base de données
            error_message = "username ou mot de passe invalide."
            return render(request, 'blog_app/login.html', {'error_message': error_message, 'form':form})
    else:
        form = forms.LoginForm()
        return render(request, 'blog_app/login.html', {"form": form})


def register_view(request):
    """This method is used to manage user registration.

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: HTTP response object that renders an HTML page template, root if the user is registered,
        he is automatically logged in,
        else, the same page template with the view context.
    """
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            try:
                new_user = models.UserModels.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                new_user.save()
                new_user.is_active = True
                user = authenticate(request, username=new_user.username, password=form.cleaned_data["password"])
                login(request, user)
                return redirect('/')
            except IntegrityError:
                form.add_error('username', 'Le nom d\'utilisateur existe déjà.')
    else:
        form = forms.RegisterForm()
    return render(request, "blog_app/register.html", {"form": form})
    

class logout_view(LogoutView):
    next_page = '/'
    
    
def post_view(request):
    """This method is used to manage post creation.

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: HTTP response object that renders an HTML page template, root if the user is the post was created,
        else, the same page template with the view context.
    """
    if request.method == 'POST':
        form = forms.CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = models.PostModels(
                username = request.user.username,
                categorie = form.cleaned_data['categorie'],
                title = form.cleaned_data['title'],
                image = form.cleaned_data['image'],
                content = form.cleaned_data['content'],
            )
            post.save()
            return redirect('/')
    else:
        form = forms.CreatePostForm()
    return render(request, "blog_app/post.html", {'form': form})


def list_posts(request):
    """Allows the display of all the messages sorted by in descending order according to the id. 

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: HTTP response object that renders an HTML page template with all the posts.
    """
    p = Paginator(models.PostModels.objects.all().order_by('-id'), 8)
    # Récupére le numéro de page à partir des paramètres GET
    page = request.GET.get('page')
    # Récupére les objets Post de la page courante
    posts = p.get_page(page)
    return render(request, "blog_app/posts.html", {'posts': posts})

def add_remove_favori(request, id):
    print("id: ",id)
    print("add remove")
    if request.user.is_authenticated:    
        if request.method == 'POST':
            post = models.PostModels.objects.get(id=id)
            if request.user in post.favoris.all():
                post.favoris.remove(request.user)
                print("supprimer")
            else:
                print("ajouter")
                post.favoris.add(request.user)
            return render( request, 'blog_app/favori_btn.html', {'post':post})

# @login_required
def add_remove_bookmark(request, id):
    print("id: ",id)
    if request.user.is_authenticated:   
        if request.method == 'POST':
            post = models.PostModels.objects.get(id=id)
            if request.user in post.bookmark.all():
                post.bookmark.remove(request.user)
                print("supprimer")
            else:
                print("ajouter")
                post.bookmark.add(request.user)
            return render( request, 'blog_app/bookmark_btn.html', {'post':post})

def post_detail(request, pk, username, categorie):
    """Retrieves the PostModels object associated with the identifier.

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.
        pk (_type_): post id.

    Returns:
        _type_: HTTP response object that renders an HTML page template with the PostModels object.
    """
    post = get_object_or_404(models.PostModels, pk=pk)
    print("username: ",post.username)
    print("username: ",username)
    by_username = models.PostModels.objects.filter(username=post.username).exclude(id__in=[post.id]).order_by('-id')[:2]
    by_categorie = models.PostModels.objects.filter(categorie=categorie).exclude(id__in=[post.id]+[post2.id for post2 in by_username]).order_by('-id')[:2]
    print("post_username: ",by_username)
    comments = models.CommentModels.objects.filter(post=post).order_by('-id')
    if request.user.is_authenticated:
        form = forms.CreateCommentForm(request.POST)
        if request.method == "POST":
            if 'add-comment' in request.POST:
                button_value = request.POST['add-comment']
                if button_value == 'pressed':
                    content = request.POST.get('content')
                    models.CommentModels.objects.create(post=post, username=username, content=content)
                    return redirect('post_detail', pk=pk, username=username, categorie=categorie)
    else:
        form = None
    
    context = {
        'first_post': post,
        'post': post,
        'by_categorie': by_categorie,
        'by_username': by_username,
        'comments': comments,
        'form': form,
    }
    print(f"----by_categorie: {by_categorie}")
    print(f"----by_username: {by_username}")
    # ici, la variable 'post' contient l'objet Post correspondant à l'id 'pk'
    return render(request, 'blog_app/post_detail.html', context)



def posts(request, filter_by, value):
    """summary
    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.
        filter_by (_type_): La variable dynamique dans l'URL qui détermine le filtre de tri à utiliser (par exemple, "username", "date" ou "categorie").
        value (_type_): La valeur à utiliser pour filtrer et trier les publications (par exemple, le nom d'utilisateur, la date ou la catégorie).

    Returns:
        _type_: _description_
    """
    print("------------------------------------------------------")
    if filter_by == 'username':
        post_list = models.PostModels.objects.filter(username=value).order_by('-id')
    elif filter_by == 'date':
        post_list = models.PostModels.objects.filter(date=value).order_by('-date')
    elif filter_by == 'categorie':
        post_list = models.PostModels.objects.filter(categorie=value).order_by('-id')
    elif filter_by == 'bookmark':
        print(request.get_full_path())
        if request.user.is_authenticated:
            post_list = models.PostModels.objects.filter(bookmark=request.user).order_by('-id')
        else:
            return redirect(reverse('login') + '?next=' + request.get_full_path())
        
    p = Paginator(post_list, 10)
    page = request.GET.get('page')
    posts = p.get_page(page)
    context = {'posts': posts, 'filter_by': filter_by, 'value': value}

    if not posts:
        context['message'] = "Empty for now, come back later"
    else:
        context['message'] = None
    
    if filter_by == 'username':
        context['username'] = value
    elif filter_by == 'date':
        context['date'] = value
    elif filter_by == 'categorie':
        context['categorie'] = value

    print("filter_by: ",filter_by)
    print("value: ",value)
    print("message: ",context['message'])
    return render(request, 'blog_app/posts.html', context)

def comments_area(request, pk):
    print("")
    print("-----esapce commentaires-----")
    print("")
    post = get_object_or_404(models.PostModels, pk=pk)
    print(post.id)
    print("request: ", request)
    # comments = models.CommentModels.objects.filter(post=post).order_by('-id')
    # print("comments: ",comments)
    print("request.POST: ",request.POST)
    print("request.method: ",request.method)
    print("request.GET: ",request.GET)
    # print("nombre: ",len(comments))
    if request.user.is_authenticated:
        if request.method == "POST":
            form = forms.CreateCommentForm(request.POST)
            if form.is_valid():
                #content = request.POST.get('content')
                username = request.user.username
                content = form.cleaned_data['content']
                print("-request: ",request)
                print("-content: ",content)
                print("id: ",post.id)
                models.CommentModels.objects.create(post=post, username=username, content=content)
            
    else:
        form = None
    comments = models.CommentModels.objects.filter(post=post).order_by('-id')
    print("nombre: ",len(comments))
    context={
        'post': post,
        'comments': comments,
        'form': form,
    }
    print("ca marche")
    for comment in comments:
        print(comment.content)
    return render(request, 'blog_app/comments.html', context)


def contact_view(request):
    print("ici")
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)

        if form.is_valid():
            print("formulaire valide")

            send_mail("send_email")

            return redirect('contact_view')
    else:
        form = forms.ContactForm()
    context = {
        'form': form,
    }
    return render(request, 'blog_app/contact.html', context)

def about_us(request):
    return render(request, "blog_app/aboutus.html")


from django.http import JsonResponse

# def search(request):
#     """This method allows you to search for objects in a database using specific search criteria.
#         search by title and username

#     Args:
#         request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

#     Returns:
#         _type_: html with all objects 
#     """
#     # récupère la requete applée 'title/username'
#     query = request.GET.get('title/username')
#     if query:
#         # récupère les objets filtrés par le titre et le nom d'utilisateur en fonction de query
#         # | opératuer de django pour combiné les requetes
#         posts = models.PostModels.objects.filter(Q(title__contains=query) | Q(username__contains=query)).order_by('-id')
#         if not posts:
#             return redirect(request.META.get('HTTP_REFERER', '/'))
        
#     # return render(request, "blog_app/posts.html", {'posts': posts})
#     data = [{'title': post.title, 'username': post.username} for post in posts]
    
#     return JsonResponse(data, safe=False) 


def search_resutls(request):
    """This method allows you to search for objects in a database using specific search criteria.
        search by title and username

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: html with all objects 
    """
    # récupère la requete applée 'title/username'
    query = request.GET.get('search')
    if query:
        # récupère les objets filtrés par le titre et le nom d'utilisateur en fonction de query
        # | opératuer de django pour combiné les requetes
        posts = models.PostModels.objects.filter(Q(title__contains=query) | Q(username__contains=query)).order_by('-id')
        if posts:
            return render(request, "blog_app/posts.html", {'posts': posts})     
    return redirect(request.META.get('HTTP_REFERER', '/'))
    


def search_recommandations(request):
    search_text = request.POST.get('search')
    # results = models.PostModels.objects.filter(Q(title__contains=search_text) | Q(username__contains=search_text)).order_by('-id')
    if search_text:
        results = models.PostModels.objects.filter(title__contains=search_text)
    else:
        results = ""
    context = {
        'results': results,
    }
    return render(request, 'blog_app/search_recommandations.html', context)
    
    
    
    
