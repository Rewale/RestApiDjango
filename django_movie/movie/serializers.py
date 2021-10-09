from rest_framework import serializers
from .models import Movie, Review, Rating, Actor


class FilterReviewSerializer(serializers.ListSerializer):
    """Фильтр комментариев, только parents"""
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ("title", "tagline", "category", 'rating_user', 'middle_star')


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод списка актеров и режиссеров"""
    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод полного описания актеров или режиссеров"""
    class Meta:
        model = Actor
        fields = "__all__"


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзыва"""

    class Meta:
        model = Review
        fields = '__all__'


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивных childern"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Cписок отзывов"""

    # Вывод вложенных комментариев
    children = RecursiveSerializer(many=True)

    class Meta:
        # Кастомный сериализатор для списков(чтобы не выводились дочерние комментарии)
        list_serializer_class = FilterReviewSerializer
        model = Review
        fields = ('name', 'text', 'children')


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полная информация о фильме"""

    # Вместо id выводим имя
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)

    # Добавим новое поле для комментариев
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        # Будут выведены все поля кроме
        exclude = ("draft",)


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователя"""
    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        # Ставим 2 переменные так как метод возвращает кортеж из созданного элемента и бул
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get('star')}
        )
        return rating



