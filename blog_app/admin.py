# blog_app/admin.py

# permet de personnaliser l'interface administrateur intégrée dans django

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserModels, PostModels, CommentModels

from .forms import CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {'fields': ('description',)}),
    )

class CustomPostAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'categorie', 'title', 'date')
    list_filter = ('user_id', 'categorie', 'title', 'date')
    search_fields = ('user_id', 'categorie', 'title', 'date')

class CustomCommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'content', 'date', 'post', 'id')
    list_filter = ('username', 'date', 'post')
    search_fields = ('username', 'date', 'post')


# Enregistrer le modèle d'utilisateur personnalisé avec le gestionnaire personnalisé
admin.site.register(UserModels, CustomUserAdmin)

admin.site.register(PostModels, CustomPostAdmin)

admin.site.register(CommentModels, CustomCommentAdmin)
