from django.contrib.auth.models import User
from rest_framework import serializers
from app.models import Post, Category


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):

    category = CategorySerializer(required=False)
    author = AuthorSerializer(required=False, read_only=True)

    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'status', 'author', 'updated', 'publication_date',
        'category']

    def create(self, validated_data):
        category = validated_data.pop('category')

        try:
            cat = Category.objects.get(name=category['name'])
        except Category.DoesNotExist:
            cat = Category.objects.create(**category)

        post = Post.objects.create(category=cat, **validated_data)
        return post
