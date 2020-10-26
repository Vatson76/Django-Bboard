from .models import SubRubric

def bboard_context_processor(request):
    """Функция, позволяющая возвращать пользователя на то же место,
    где он находялся при открытии объявления."""
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    context['keyword'] = ''
    context['all'] = ''
    if 'keyword' in request.GET:  # если ключевое слово присутствует в запросе
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':  #если страница первая, то ничего менять не надо
            if context['all']:
                context['all'] += '&page=' + page # формирование нового урл
            else:
                context['all'] = '?page=' + page
    return context




