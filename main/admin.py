from django.contrib import admin
import datetime

from .models import AdvUser, SuperRubric, SubRubric, Bb, AdditionalImage, Comment
from .utilities import send_activation_notification
from .forms import SubRubricForm


def send_activation_notifications(modeladmin, request, queryset):
    """Функция для отправки сообщения активации пользователю"""
    for rec in request:
        if not rec.is_activated: #если пользователь не активирован, отправить ему сообщение
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с оповещениями отправлены')
send_activation_notifications.short_description = 'Отправка писем с оповещениями об активации'

class NonactivatedFilter(admin.SimpleListFilter):

    """Фультр в панели администрации,  разделяющий пользователей по категориям"""

    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):  # разделение пользователей по активации
        return (
                ('activated', 'Прошли'),
                ('threedays', 'Не прошли более 3 дней'),
                ('week', 'Не прошли более 7 дней'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val =='activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)

        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)

class AdvUserAdmin(admin.ModelAdmin):
    '''Страница объектов пользователей'''

    list_display = ('__str__', 'is_activated', 'date_joined')  #показывать на странице объектов следующие элементы
    search_fields = ('username', 'email', 'first_name', 'last_name')  #поля, доступные для поиска
    list_filter = (NonactivatedFilter,)   #фильтр, применяемый к is activated
    fields = (('username', 'email'), ('first_name', 'last_name'),  # поля, отображаемые при взаимодействии с объектом, обьекты в скобках группируются и выводятся в одной строке, каждй объект  в списке выводится на новой строке
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'), 'groups',
              'user_permissions', ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')   #поля,  доступные только для чтения. Их нельзя изменить
    actions = (send_activation_notifications,)


class SubRubricInline(admin.TabularInline):  #Объекты подрубрики
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):  #Объекты надрубрики
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)

admin.site.register(SuperRubric, SuperRubricAdmin)  #Регистрация модели надрубрики на административном сайте

class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


admin.site.register(SubRubric, SubRubricAdmin)


admin.site.register(AdvUser, AdvUserAdmin)  #Зарегистрировали модель пользователя


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    fields = (('rubric', 'author'), 'title', 'content', 'price', 'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline,)

admin.site.register(Bb, BbAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'content', 'is_active')
    search_fields = ('author',)
    fields = ('author', 'content', 'is_active')
    readonly_fields = ('created_at',)

admin.site.register(Comment, CommentAdmin)
