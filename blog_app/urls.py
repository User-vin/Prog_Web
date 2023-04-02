# blog/blog_app/urls.py

# dénifi les addresses urls pour accéder aux views 

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index_view, name="index"),
    path('logout/', views.logout_view.as_view(), name="logout"),
    path('login/',views.login_view, name="login"),

    path('register/',views.register_view, name="register"),
    path('post/',views.post_view , name="post"),
    path('posts/',views.list_posts, name="list_posts"),
    
    #-----
    
    
    path('favori/<int:id>/', views.add_remove_favori, name='add_remove_favori'),
    path('bookmark/<int:id>/', views.add_remove_bookmark, name='add_remove_bookmark'),
    path('comments/<int:pk>/', views.comments_area, name='comments_area'),

    #-----
    
    path('posts/<str:filter_by>/<str:value>/', views.posts, name="posts_filter"),
    path('post_display/<int:pk>/<str:username>/<str:categorie>/', views.post_detail, name='post_detail'),

    path('contact/', views.contact_view, name='contact_view'),
    path('about-us/', views.about_us, name="about_us"),
    
    path('search-results/', views.search_resutls, name="search-results"),
    path('search-recommendations/', views.search_recommandations, name="search-recommandations"),

    # sidebar pages
    path('account/', views.account_view, name="account"),
    path('parameters/', views.parameters_view, name="parameters"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # static permet de créer une route entre MEDIA_URL et MEDIA_ROOT, 
    # c'est à dire une route entre l'url et le fichier physique contenant les fichiers multimédias
    

