from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title

from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)

User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    username = serializer.validated_data["username"]

    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        if User.objects.filter(email=email).exists():
            return Response(
                {"email": ["Пользователь с таким email уже существует."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {
                    "username": [
                        "Пользователь с таким username уже существует."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        User.objects.create_user(username=username, email=email)
        user = User.objects.get(username=username, email=email)

    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        "Код подтверждения YaMDb",
        f"Ваш код подтверждения: {confirmation_code}",
        "from@example.com",
        [email],
        fail_silently=False,
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    confirmation_code = serializer.validated_data["confirmation_code"]

    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {"detail": "Неверный код подтверждения."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = AccessToken.for_user(user)
    return Response({"token": str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    http_method_names = ["get", "post", "patch", "delete"]

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        if request.method == "GET":
            serializer = UserMeSerializer(request.user)
            return Response(serializer.data)
        serializer = UserMeSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryViewSet(
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score")).order_by(
        "id"
    )
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        queryset = Title.objects.annotate(
            rating=Avg("reviews__score")
        ).order_by("id")
        genre_slug = self.request.query_params.get("genre")
        category_slug = self.request.query_params.get("category")
        name = self.request.query_params.get("name")
        year = self.request.query_params.get("year")

        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if year and year.isdigit():
            queryset = queryset.filter(year=int(year))

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    )
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
            title_id=self.kwargs.get("title_id"),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get("review_id"),
            title_id=self.kwargs.get("title_id"),
        )
        serializer.save(author=self.request.user, review=review)
