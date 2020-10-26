from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm, BbForm, AIFormSet, UserCommentForm, GuestCommentForm
from .models import AdvUser, SubRubric, Bb, Comment
from .utilities import signer


def index(request):
    """Код основной страницы сайта, просто загружает шаблон"""
    bbs = Bb.objects.filter(is_active=True)[:10]
    context = {'bbs': bbs}  #в этой переменной хранятся все переменные для шаблонизатора django
    return render(request, 'main/index.html', context)  #функция рендер создает страницу из шаблона


def other_page(request, page):
    """Переход на следующую страницу объявлений"""
    try:
        template = get_template('main/' + page + '.html')  #формируем юрл
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class BBLoginView(LoginView):
    """ Код страницы входа пользователя, используется уже готовый класс и указывается только имя шаблона"""
    template_name = 'main/login.html'


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


@login_required  #декоратор, проверяющий выполнил ли пользователь вход
def profile(request):
    """код страницы профиля, доступен только пользователям, вполнившим вход"""
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs':bbs}
    return render(request, 'main/profile.html', context)


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """страница смены данных пользователя"""

    model = AdvUser  # используемая модель
    template_name = 'main/change_user_info.html'  # шаблон
    form_class = ChangeUserInfoForm  # форма
    success_url = reverse_lazy('main:profile')  # переход при успешном действии
    success_message = 'Личные данные пользователя изменены'  # вывод сообщения при успеном действии

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk   # получаем первичный ключ пользователя для возможности смены данных
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)




class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')

class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    """Функция активации пользователя"""
    try:
        username = signer.unsign(sign)  # проверка подписанного идентификатора(получение имени пользователя, т.к. для подписи используется именно оно)
    except BadSignature:
        return render(request, 'main/bad_signature.html')  # формируем страницу с ошибкой

    user = get_object_or_404(AdvUser, username=username) # получаем данные из бд или ошибку если пусто

    if user.is_activated:  #если уже активирован переход на соотв. страницу
        template = 'main/user_is_activated.html'

    else:  #если нет - активируем
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    """Страница удаления пользователя"""
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):  # снова получаем первичный ключ пользователя через диспатч
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post (self, request, *args, **kwargs):
        logout(request)  # выход пользователя
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')  # вывод сообщения после удачного выполнения действия

        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id) # вовзращаем найденного пользователя


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):  #основан на уже готовых классах
    """страница смены пароля"""

    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'


class BBPasswordResetView(LoginRequiredMixin, PasswordResetView):  #основан на уже готовых классах
    """страница сброса пароля"""

    template_name = 'main/password_reset.html'
    success_url = reverse_lazy('main:password_reset_done')
    subject_template_name = "registration/reset_subject.txt"
    email_template_name = "registration/reset_email.html"

class BBPasswordResetDoneView(LoginRequiredMixin, PasswordResetDoneView):  #основан на уже готовых классах
    """страница принятого запроса сброса пароля"""

    template_name = 'main/password_reset_done.html'

class BBPasswordResetCompleteView(PasswordResetCompleteView):  #основан на уже готовых классах
    """страница удачно выполненого сброса пароля"""

    template_name = 'main/password_reset_complete.html'

def by_rubric(request, pk):
    """Функция для выыведения объявлений связанных с выбранной рубрикой"""
    rubric = get_object_or_404(SubRubric, pk=pk)  #Получаем название рубрики
    bbs = Bb.objects.filter(is_active=True, rubric=pk)  #Получаем все объявления, связанные с рубрикой
    if 'keyword' in request.GET:  #Если осуществляется поиск по ключевому слову
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)  #использование класса Q для применения сложной фильтрации
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)  # максимум 2 объявления на страницу
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)


def detail (request, rubric_pk, pk):
    """ССодержание объявления"""
    bb = Bb.objects.get(pk=pk)  # объект объявления
    ais = bb.additionalimage_set.all()  # изображения, связанные с объявлением
    comments = Comment.objects.filter(bb=pk, is_active=True)  # комментарии, связанные с объявлением(только с флажком активных)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:  # если пользователь активирован
        initial['author'] = request.user.username  # Автоматом заполняем поле автора
        form_class = UserCommentForm  # выводим пользовательскую форму для комментариев(не требует капчу)
    else:
        form_class = GuestCommentForm  # в противном случае форма гостя. ТРЕБУЕТ КАПЧУ
    form = form_class(initial=initial)
    if request.method == 'POST':  #Если поступил пост запрос - добавление комментария и сохранение его в БД
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)

def detail1 (request, pk):  #Сделал для деталей на главной странице. Вроде как костыль
    bb = Bb.objects.get(pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)

@login_required  # только для пользователей, выполнивших вход
def profile_bb_detail(request, pk):
    """Страница профиля пользователя"""
    bb = get_object_or_404(Bb, pk=pk)  # Все связанные с ним объявления
    ais = bb.additionalimage_set.all()  #Изображения объявлений
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/profile_bb_detail.html', context)


@login_required
def profile_bb_add(request):
    """Функция для добавления объявления пользователем"""
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)  #В форму необходимо передавать 2 аргументом request.FILES, чтобы не потерять изображения
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)  #Необходимо для добавления изображений в объявленгие
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')

                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_add.html', context)


@login_required
def profile_bb_change(request, pk):
    """Функция для изменения объявления пользователем"""
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')

                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_change.html', context)


# @login_required
# def profile_bb_delete(request, pk): Зачем-то нужен пост, хотя на странице просто кнопка. Создает лишнюю страницу? зачем?
#     Ниже написал функцию, где удаление происходит просто нажатием на кнопку, после чего объявление удаляется и выводится всплывающее уведомление об удалении
#     bb = get_object_or_404(Bb, pk=pk)
#     if request.method == 'POST':
#         bb.delete()
#         messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
#         return redirect('main:profile')
#     else:
#         context = {'bb': bb}
#         return render(request, 'main/profile_bb_delete.html', context)

@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    bb.delete()
    messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
    return redirect('main:profile')




