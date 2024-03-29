# blog/bloag_app/forms.py

# défini des classes de formulaires
# permet de valider les données entrées par l'utilisateur
# permet d'envoyer des donnés du front end vers le back end

from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor_uploader.fields import RichTextUploadingField
from . import models

from django.contrib.auth.forms import UserChangeForm

# permet de changer les attributs d'un objets utilisateur
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = models.UserModels
        fields = '__all__'

# permet de modifier le contenu des attributs dans l'objet utilisateur 
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.UserModels
        fields = ['username', 'email' , 'description']

    description = forms.Textarea()


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), required=True)
    email = forms.EmailField(widget=forms.EmailInput(), label='E-mail', required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

class CreatePostForm(forms.ModelForm):
    
    class Meta:
        model = models.PostModels
        # champs qui s'affichent automatiquement si utilisation de {{ form.as_p }}
        fields = ['title', 'image', 'content', 'categorie']  
        labels = { # libellés remplacés par ''
            'title': '',
            'categorie': 'Category',
            'content': 'Content',
            'image': 'Image',
        }
        widgets = {  
            'title': forms.TextInput(attrs={'placeholder': 'Title', 'id': 'id_write_title'}), # affiche du texte dans le champ
            'content' : forms.CharField(widget=CKEditorUploadingWidget()),

        }
        label_suffix = ''
    
class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = models.CommentModels
        fields = ['content']
        labels = {
            'content': ''
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your comment here', 'id': 'id_content'}),
        }

class ContactForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    content = forms.CharField(widget=forms.Textarea)
         

         
         