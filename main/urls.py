from django.urls import path

from django.views.decorators.cache import never_cache
from django.conf.urls.static import static, serve
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from bboard import settings

from .views import detail, detail1, profile_bb_detail
from .views import index, other_page, BBLoginView, profile, BBLogoutView, ChangeUserInfoView, BBPasswordChangeView, RegisterUserView, RegisterDoneView, by_rubric
from .views import user_activate, DeleteUserView, BBPasswordResetView, BBPasswordResetDoneView, BBPasswordResetCompleteView, profile_bb_add, profile_bb_change, profile_bb_delete


app_name = 'main'
urlpatterns = [

    path('detail/<int:pk>/', detail1, name='detail1'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),

    path('', index, name='index'),

    path('accounts/login/', BBLoginView.as_view(), name='login'),

    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),

    path('accounts/profile/change/<int:pk>', profile_bb_change, name='profile_bb_change'),
    path('accounts/profile/delete/<int:pk>', profile_bb_delete, name='profile_bb_delete'),
    path('accounts/profile/add', profile_bb_add, name='profile_bb_add'),
    path('accounts/profile/<int:pk>', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),

    path('accounts/password/change', BBPasswordChangeView.as_view(), name='password_change'),

    path('accounts/register/done', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),


    path('accounts/password_reset/', BBPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name = 'main/password_reset_confirm.html', post_reset_login = False,
                                                                                      success_url = reverse_lazy('main:password_reset_complete')),
                                                                                      name='password_reset_confirm'),
    path('accounts/password_reset/done', BBPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/password/reset/done/', BBPasswordResetCompleteView.as_view(), name='password_reset_complete'),




]

if settings.DEBUG:
    urlpatterns.append(path('static/<path:path>', never_cache(serve)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)