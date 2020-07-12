from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


# Форма регистрации пользователя
class UserRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'confirm_password'
        ]

    # Проверка формы
    def clean(self, *args, **kwargs):
        username_qs = User.objects.filter(username=self.cleaned_data['username'])
        if username_qs.exists():
            raise forms.ValidationError("User has been already exist.")
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError('Passwords must match.')
        if len(self.cleaned_data['password']) < 8:
            raise forms.ValidationError('Password must be at least 8 characters')
        super(forms.ModelForm, self).clean(*args, **kwargs)


class ChangePassword(forms.ModelForm):
    username = forms.CharField(widget=forms.HiddenInput)
    password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'new_password', 'confirm_password'
        ]

    def clean(self, *args, **kwargs):
        user = User.objects.get(username=self.cleaned_data['username'])

        if not user.check_password(self.cleaned_data.get('password')):
            raise forms.ValidationError(('Password does not correct'))
        if self.cleaned_data['new_password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError(('Passwords must match.'))
        if len(self.cleaned_data['new_password']) < 8:
            raise forms.ValidationError(('Password must be at least 8 characters'))
        super(forms.ModelForm, self).clean(*args, **kwargs)
