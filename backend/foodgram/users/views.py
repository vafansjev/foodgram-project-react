from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.pagination import CustomPagesPaginator
from .models import Subscription, User
from .serializers import SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    """
    Представление для работы с подписками пользователей
    """
    pagination_class = CustomPagesPaginator

    @action(
        detail=False,
        methods=['GET'],
        url_name="me",
        url_path="me",
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='subscribe'
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response({
                    'errors': 'Нельзя подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST)
            subscription = Subscription.objects.create(
                user=user,
                author=author
                )
            serializer = SubscribeSerializer(
                subscription,
                context={'request': request}
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user == author:
                return Response({
                    'errors': 'Нельзя подписываться на самого себя'
                }, status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Subscription.objects.filter(
                user=user, author=author
                )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)