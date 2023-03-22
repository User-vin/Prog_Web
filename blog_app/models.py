# blog/blog_app/models.py

# permet de définir la structure de base de donnée

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from ckeditor.fields import RichTextField

# gestionnaire par défaut plus disponible car User remplacé par une version personnalisée (UserModels)
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """
        Créé et sauvegarde un utilisateur avec l'email et le mot de passe donnés
        """
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Créé et sauvegarde un super utilisateur avec l'email et le mot de passe donnés
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class UserModels(AbstractUser):
    biographie = models.TextField(blank=True, null=True)
    
    objects = UserManager()
    

class PostManager(models.Manager):
    def create_post(self, username, categorie, title, content, image):
        post = self.model(
            username = username,
            categorie = categorie,
            title = title,
            content = content,
            image = image,
        )
        post.save(using=self._db)
        return post


    
class PostModels(models.Model): # structure d'un article de blog
    
    class Categories(models.TextChoices): # permet de définir des choix textuels pour la catégorie
        Healthy_Food = 'Healthy Food' # Healthy Food ... sont les clés classées dans la BDD pour chaque catégories
        Organic_Cuisine = 'Organic Cuisine'
        Vegetarian_Food = 'Vegetarian Food'
       
    username = models.CharField(max_length=30, blank=False) 
    categorie = models.fields.CharField(choices=Categories.choices, max_length=15)
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=30, blank=False)
    # content = models.TextField(blank=False)
    content = RichTextField(blank=False, null=True)
    image = models.ImageField(upload_to='posts_images/', blank=False, null=True)
    favoris = models.ManyToManyField(UserModels, blank=True, related_name='favoris')
    bookmark = models.ManyToManyField(UserModels, blank=True, related_name='bookmark')
    testcontent = models.FileField(upload_to='posts_image/', blank=False)
    objects = PostManager()
    
    

class CommentModels(models.Model):
    username = models.CharField(max_length=30, blank=False)
    date = models.DateField(auto_now_add=True)
    content = models.TextField(max_length=200, blank=False)
    post = models.ForeignKey(PostModels, on_delete=models.CASCADE, related_name='comments')

