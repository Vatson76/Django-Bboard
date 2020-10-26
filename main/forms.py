from django import forms
from .models import AdvUser
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import user_registrated, SuperRubric, SubRubric, Bb, AdditionalImage, Comment
from django.forms import inlineformset_factory
from captcha.fields import CaptchaField



class ChangeUserInfoForm(forms.ModelForm):
    """Форма для изменения профиля"""
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')


class RegisterUserForm(forms.ModelForm):
    """Форма регистрации нового пользователя"""
    email = forms.EmailField(required=True,  #поле для ввода эмэила
                             label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,  #поле пароля, с виджетом, скрывающим пароль
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль(повторно)', widget=forms.PasswordInput,  # повторный ввод пароля
                                help_text='Введите тот же самый пароль еще раз для проверки')

    def clean_password(self):
        """метод проверки введенного пароля набезопасность"""
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)  #валидация пароля. Исключает маленькие пароли, типичные пароли, и слабозащищенные пароли.
        return password1

    def clean(self):
        """метод проверки одинаково введенных паролей"""
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        """метод для сохранения пользователя в БД"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1']) #установка пароля
        user.is_active = False  #при регистрации автоматический вход не производится
        user.is_activated = False  #необходимо подтвердить регистрацию
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')


class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(),
                                          empty_label=None,
                                          label='Надрубрика', required=True)
    class Meta:
        model = SubRubric
        fields = '__all__'


class SearchForm(forms.Form):
    """форма с полем, находящаясь в углу в разделе объявлений в каждой рубрике. Необходима для поиска по ключевым словам"""
    keyword = forms.CharField(required=False, max_length=20, label='')


class BbForm(forms.ModelForm):
    """Форма для создания нового объявления"""
    class Meta:
        model = Bb
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

AIFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class UserCommentForm(forms.ModelForm):
    """Форма для добавления комментария в объявление"""
    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'bb': forms.HiddenInput}


class GuestCommentForm(forms.ModelForm):
    """Форма для добваления пароля для гостей. Им необходимо ввести капчу"""
    captcha = CaptchaField(label='Введите текс с картинки', error_messages={'invalid': 'Неправильный текст'})

    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'bb': forms.HiddenInput}



