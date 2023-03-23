from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms


User = get_user_model()


class CreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    User._meta.get_field('email')._unique = True

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
