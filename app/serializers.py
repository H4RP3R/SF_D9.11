from django.contrib.auth.models import User
from rest_framework import serializers
from app.models import Post, Category
import json


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class CategorySerializer(serializers.ModelSerializer):

    name = serializers.CharField(max_length=255, required=False)
    slug = serializers.SlugField(required=False)

    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        if validated_data['name'] and validated_data['slug']:
            return Category.objects.create(**validated_data)
        return None


class CategorySerializerWithPosts(serializers.ModelSerializer):

    posts = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'posts']


class PostSerializer(serializers.ModelSerializer):

    category = CategorySerializer(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'status', 'updated', 'publication_date',
                  'author', 'category']

    def create(self, validated_data):
        category = validated_data.pop('category')
        if 'name' in category:
            try:
                cat = Category.objects.get(name=category['name'])
            except Category.DoesNotExist:
                cat = Category.objects.create(**category)
        else:
            cat = None

        username = validated_data.pop('author')
        try:
            author = User.objects.get(username=username)
        except User.DoesNotExist:
            author = None

        post = Post.objects.create(category=cat, author=author, **validated_data)
        return post

    @property  # dynamically updates choices in the author field
    def author(self):
        return serializers.ChoiceField(required=True, blank=False,
                                       choices=[(user.username, user.username)
                                                for user in User.objects.all()])

    def to_representation(self, instance):
        if instance.author:
            author = {
                'id': instance.author.id,
                'username': instance.author.username,
            }
        else:
            author = None

        if instance.category:
            category = {
                'id': instance.category.id,
                'slug': instance.category.slug,
                'name': instance.category.name,
            }
        else:
            category = None

        data = {
            'id': instance.id,
            'title': instance.title,
            'slug': instance.slug,
            'content': instance.content,
            'status': instance.status,
            'updated': instance.updated,
            'publication_date': instance.publication_date,
            'author': author,
            'category': category,
        }
        return data
