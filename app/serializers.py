from django.contrib.auth.models import User
from rest_framework import serializers
from app.models import Post, Category
import json


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategorySerializerWithPosts(serializers.ModelSerializer):

    posts = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'posts']


class PostSerializer(serializers.ModelSerializer):

    category = CategorySerializer(required=False)
    author = serializers.ChoiceField(
        choices=[(user.username, user.username) for user in User.objects.all()])

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'status', 'updated', 'publication_date',
                  'author', 'category']

    def create(self, validated_data):
        category = validated_data.pop('category')
        try:
            cat = Category.objects.get(name=category['name'])
        except Category.DoesNotExist:
            cat = Category.objects.create(**category)

        username = validated_data.pop('author')
        author = User.objects.get(username=username)
        post = Post.objects.create(category=cat, author=author, **validated_data)
        return post
