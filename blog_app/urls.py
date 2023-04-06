# blog_app/urls.py

# permet de générer les urls de l'application
# asscie url et vue

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index_view, name="index"),
    # url: 'logout/' , la vue: views.logout_view.as_view(), 
    # nom appelable dans un htlml au autre méthode: logout
    path('logout/', views.logout_view.as_view(), name="logout"),
    
    # log regis
    path('login/',views.login_view, name="login"),
    path('register/',views.register_view, name="register"),
    
    # posts
    path('post/',views.post_view , name="post"),
    # <str:filter_by> prend un string, <value> prend n'importe quel type
    path('posts/<str:filter_by>/<value>/', views.posts, name="posts_filter"),
    path('post_display/<int:pk>/<str:user_id>/<str:categorie>/', views.post_detail, name='post_detail'),

    #-----
    path('favori/<int:id>/', views.add_remove_favori, name='add_remove_favori'),
    path('bookmark/<int:id>/', views.add_remove_bookmark, name='add_remove_bookmark'),
    path('comments/<int:pk>/', views.comments_area, name='comments_area'),
    #-----
    
    path('contact/', views.contact_view, name='contact_view'),
    path('about-us/', views.about_us, name="about_us"),
    
    # search
    path('search-recommendations/', views.search_recommandations, name="search-recommandations"),

    # sidebar pages
    path('account/<user_id>/', views.account_view, name="account"),
    path('parameters/', views.parameters_view, name="parameters"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # static permet de créer une route entre MEDIA_URL et MEDIA_ROOT, 
    # c'est à dire une route entre l'url et le fichier physique contenant les fichiers multimédias
    

