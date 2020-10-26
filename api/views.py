from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.generics import RetrieveAPIView

from main.models import Bb, Comment
from .serializers import BbSerializer, BbDetailSerializer, CommentSerializer

@api_view(['GET'])  #проверка на тип запроса
def bbs(request):
    if request.method == 'GET':
        bbs = Bb.objects.filter(is_active=True)[:10]
        serializer = BbSerializer(bbs, many=True)
        return Response(serializer.data)


class BbDetailView(RetrieveAPIView):
    queryset = Bb.objects.filter(is_active=True)
    serializer_class = BbDetailSerializer


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticatedOrReadOnly,))  # действия доступны только активированным пользователям, остальным только чтение
def comments(request, pk):
    if request.method == 'POST':  #если получен пост запрос - добавление нового комментария
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    else:  # если нет, то просто просмотр
        comments = Comment.objects.filter(is_active=True, bb=pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
