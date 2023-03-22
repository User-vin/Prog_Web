

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserModels, PostModels, CommentModels

class CustomUserAdmin(UserAdmin):
    # Personnaliser les champs affichés dans la liste des utilisateurs
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

class CustomPostAdmin(admin.ModelAdmin):
    list_display = ('username', 'categorie', 'title', 'date')
    list_filter = ('username', 'categorie', 'title', 'date')
    search_fields = ('username', 'categorie', 'title', 'date')

class CustomCommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'content', 'date', 'post', 'id')
    list_filter = ('username', 'date', 'post')
    search_fields = ('username', 'date', 'post')


# Enregistrer le modèle d'utilisateur personnalisé avec le gestionnaire personnalisé
admin.site.register(UserModels, CustomUserAdmin)

admin.site.register(PostModels, CustomPostAdmin)

admin.site.register(CommentModels, CustomCommentAdmin)
