# blog_app/views.py

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
    # Parmis les objets PostModels triés par le nombre de favoris par ordre décroissant. 
    # Récupérer les deux derniers objets Post
    most_preferred = models.PostModels.objects.annotate(num_favoris=Count('favoris')).order_by('-num_favoris')[:2]   
    
    first_post = most_preferred[0]
    second_post = most_preferred[1]
    posts = models.PostModels.objects.exclude(id__in=[first_post.id, second_post.id]).order_by('-id')[:3]
    posts2 = models.PostModels.objects.annotate(num_favoris=Count('bookmark')).exclude(id__in=[first_post.id, second_post.id]+[post.id for post in posts]).order_by('-num_favoris')[:3]
    
    context = {
        'first_post': first_post,
        'second_post': second_post,
        'posts': posts,
        'posts2': posts2,
    }
    # Rendre le template blog_app/index.html
    # context contient les variable utilisable dans le html
    return render(request, 'blog_app/index.html', context)
    
    
def login_view(request):
    """This method is used to manage the connection of users.

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.

    Returns:
        _type_: HTTP response object that renders an HTML page template, root if the user is logged in
        else, the same page template with the view context.
    """
    if request.method == "POST": # vérifie si c'est une requete POST 
        username = request.POST.get('username') # extrait de la requete POST la valeur associée a username
        password = request.POST.get('password')
        # si les paramètres fournis correspondent à un utilisateur, il est alors connecté
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # utilisateur trouvé dans la base de donnée
            # connectez l'utilisateur
            login(request, user)
            if request.user.is_authenticated:
                redirect_to = request.GET.get('next', '')
                return HttpResponseRedirect(redirect_to) 
        else:
            form = forms.LoginForm() # crée une instance de LoginForm()
            # utilisateur non trouvé dans la base de données
            error_message = "username ou mot de passe invalide."
            return render(request, 'blog_app/log_regis/login.html', {'error_message': error_message, 'form':form})
    else:
        form = forms.LoginForm()
        return render(request, 'blog_app/log_regis/login.html', {"form": form})


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
        # définie une instance de RegisterForm initialisé avec les informations de request.POST
        form = forms.RegisterForm(request.POST) 
        if form.is_valid():
            try:
                new_user = models.UserModels.objects.create_user(
                    # récuppère la valeur du champ username
                    # champ rempli par l'utilisateur
                    # néttoie la valeur, pour etre sur que la valeur est valide
                    username=form.cleaned_data['username'], 
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    description="",
                )
                new_user.save() # enregistre l'utilisateur
                new_user.is_active = True # connecte l'utilisateur
                user = authenticate(request, username=new_user.username, password=form.cleaned_data["password"])
                login(request, user)
                return redirect('/')
            except IntegrityError:
                form.add_error('username', 'Le nom d\'utilisateur existe déjà.')
    else:
        form = forms.RegisterForm()
    return render(request, "blog_app/log_regis/register.html", {"form": form})
    

class logout_view(LogoutView):
    next_page = '/'
    
@login_required
def account_view(request, user_id):
    """This view is used to display the user's account information such as the number of posts, 
    bookmarks, and favorites that the user has created. 

    Args:
        request (_type_): _description_
        user_id (int): user id

    Returns:
        _type_: _description_
    """
    user = request.user # permet d'obtenir l'instance de user
    if user.id != user_id:
        # récuppère un objet UserModels en fonction de user_id 
        # ou retourne une erreur 404
        user = get_object_or_404(models.UserModels, id=user_id)
    posts_count = models.PostModels.objects.filter(user_id=user.id).count
    bookmarked_count = models.PostModels.objects.filter(bookmark=user).count
    fav_count = models.PostModels.objects.filter(favoris=user).count
    context = {
        'user': user,
        'posts_count': posts_count,
        'bookmarked_count': bookmarked_count,
        'fav_count': fav_count,
    }
    return render(request, "blog_app/sidebar/account.html", context)


@login_required
def parameters_view(request):
    """This view is used to display the user's profile information and allows the user to update it. 
        It also displays the number of posts, bookmarks, and favorites that the user has created. 
        This view is accessible only to authenticated users 

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    user = request.user
    form = forms.UserUpdateForm(instance=user)
    posts_count = models.PostModels.objects.filter(user_id=user.id).count
    bookmarked_count = models.PostModels.objects.filter(bookmark=user).count
    fav_count = models.PostModels.objects.filter(favoris=user).count
    if request.method == 'POST':
        form = forms.UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('account', user_id=user.id)
    context = {
        'form': form,
        'posts_count': posts_count,
        'bookmarked_count': bookmarked_count,
        'fav_count': fav_count,
    }
    return render(request, "blog_app/sidebar/parameters.html", context)

@login_required
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
                user_id=request.user,
                categorie = form.cleaned_data['categorie'],
                title = form.cleaned_data['title'],
                image = form.cleaned_data['image'],
                content = form.cleaned_data['content'],
            )
            post.save()
            return redirect('/')
    else:
        form = forms.CreatePostForm()
    return render(request, "blog_app/post/post.html", {'form': form})


def add_remove_favori(request, id):
    if request.user.is_authenticated:    
        if request.method == 'POST':
            post = models.PostModels.objects.get(id=id)
            if request.user in post.favoris.all():
                post.favoris.remove(request.user)
            else:
                post.favoris.add(request.user)
            return render( request, 'blog_app/favori_btn.html', {'post':post})


def add_remove_bookmark(request, id):
    if request.user.is_authenticated:   
        if request.method == 'POST':
            post = models.PostModels.objects.get(id=id)
            if request.user in post.bookmark.all():
                post.bookmark.remove(request.user)
            else:
                post.bookmark.add(request.user)
            return render( request, 'blog_app/bookmark_btn.html', {'post':post})

def post_detail(request, pk, user_id, categorie):
    """Retrieves the PostModels object associated with the identifier.

    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.
        pk (_type_): post id.

    Returns:
        _type_: HTTP response object that renders an HTML page template with the PostModels object.
    """
    post = get_object_or_404(models.PostModels, pk=pk)
    by_username = models.PostModels.objects.filter(user_id=post.user_id.id).exclude(id__in=[post.id]).order_by('-id')[:2]
    by_categorie = models.PostModels.objects.filter(categorie=categorie).exclude(id__in=[post.id]+[post2.id for post2 in by_username]).order_by('-id')[:2]
    comments = models.CommentModels.objects.filter(post=post).order_by('-id')
    if request.user.is_authenticated:
        form = forms.CreateCommentForm(request.POST)
        if request.method == "POST":
            if 'add-comment' in request.POST:
                button_value = request.POST['add-comment']
                if button_value == 'pressed':
                    content = request.POST.get('content')
                    models.CommentModels.objects.create(post=post, content=content)
                    return redirect('post_detail', pk=pk, username=user_id, categorie=categorie)
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
    # ici, la variable 'post' contient l'objet Post correspondant à l'id 'pk'
    return render(request, 'blog_app/post/post_detail.html', context)


def posts(request, filter_by, value):
    """responsible for rendering the list of all posts according to the filter specified in the URL
    Args:
        request (_type_): Contains information about the HTTP request that was sent by the client and allows to interact with the data sent in the request.
        filter_by (_type_): La variable dynamique dans l'URL qui détermine le filtre de tri à utiliser (par exemple, "username", "date" ou "categorie").
        value (_type_): La valeur à utiliser pour filtrer et trier les publications (par exemple, le nom d'utilisateur, la date ou la catégorie).

    Returns:
        _type_: _description_
    """
    first = request.GET.get('first', "True") # récuppère la valeur de first sinon donne la valeur True
    page_number = int(request.GET.get('current_page',2))
    search_text = None
    if first == "False":
        page_number+=1
    if filter_by == 'username':
        post_list = models.PostModels.objects.filter(user_id=value).order_by('-id')
    elif filter_by == 'other':  
        search_text = request.GET.get('search')
        post_list = models.PostModels.objects.filter(Q(title__icontains=search_text)).order_by('-id')
        # user_name = models.UserModels.objects.filter(Q(username__icontains=search_text)).order_by('-id')
    elif filter_by == 'all':
        post_list = models.PostModels.objects.all().order_by('-id')
    elif filter_by == 'date':
        post_list = models.PostModels.objects.filter(date=value).order_by('-date')
    elif filter_by == 'categorie':
        post_list = models.PostModels.objects.filter(categorie=value).order_by('-id')
    elif filter_by == 'bookmark':
        if request.user.is_authenticated:
            post_list = models.PostModels.objects.filter(bookmark=request.user).order_by('-id')
        else:
            return redirect(reverse('login') + '?next=' + request.get_full_path())
    elif filter_by == 'favorite':
        if request.user.is_authenticated:
            post_list = models.PostModels.objects.filter(favoris=request.user).order_by('-id')
        else:
            return redirect(reverse('login') + '?next=' + request.get_full_path())
    elif filter_by == 'myPosts':
        if request.user.is_authenticated:
            post_list = models.PostModels.objects.filter(user_id=value).order_by('-id')
        else:
            return redirect(reverse('login') + '?next=' + request.get_full_path())
    else:
        post_list = ""
        
    p = Paginator(post_list, 4) # crée une pagination avec 4 éléments de post_list par page
    page = request.GET.get('page') # récuppère le numéro la page actuelle 
    posts = p.get_page(page) # récuppère la page actuelle
    context = {
        'posts': posts, 
        'filter_by': filter_by, 
        'value': value,
        'page_max': p.num_pages + 1,
        'page_number': page_number,
        }
    
    if search_text != None:
        context['search_text'] = search_text
    
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
    return render(request, 'blog_app/post/posts.html', context)

def comments_area(request, pk):
    """ handles the creation and retrieval of comments for a specific blog post

    Args:
        request (_type_): _description_
        pk (_type_): primary key, id combinaison unique 

    Returns:
        _type_: _description_
    """
    post = get_object_or_404(models.PostModels, pk=pk)
    if request.user.is_authenticated:
        if request.method == "POST":
            form = forms.CreateCommentForm(request.POST)
            if form.is_valid():
                username = request.user.username
                content = form.cleaned_data['content']
                models.CommentModels.objects.create(post=post, username=username, content=content)
    else:
        form = None
    comments = models.CommentModels.objects.filter(post=post).order_by('-id')
    context={
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog_app/comments.html', context)


def contact_view(request):
    """handles the submission of a contact form

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']
            send_mail(
                'Nouveau message de {}'.format(username),
                content,
                email,
                ['progweb43@gmail.com'], # email du destinataire
            )
            return redirect('contact_view')
    else:
        form = forms.ContactForm()
    context = {
        'form': form,
    }
    return render(request, 'blog_app/contact.html', context)


def about_us(request):
    return render(request, "blog_app/aboutus.html")    


def search_recommandations(request):
    """show recommendation based on the user's search

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    print("-----dedans-----")
    search_text = request.POST.get('search')
    print(search_text)
    if search_text:
        print("--if--")
        results = models.PostModels.objects.filter(title__contains=search_text)
        users = models.UserModels.objects.filter(username__contains=search_text)
        print(results)
        print(users)
    else:
        results = ""
        users = ""
    context = {
        'results': results,
        'users': users,
    }
    print("-----dehors-----")
    return render(request, 'blog_app/search_recommandations.html', context)
    
    
    
    
