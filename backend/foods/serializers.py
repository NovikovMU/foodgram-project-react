from rest_framework import serializers

from .models import Ingredients, Receipts, ReceiptsIngredients, ReceiptsTags, Tags
from users.serializers import UserSerializer

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')



class ReceiptsIngredientsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(source='ingredients.measurement_unit')
    class Meta:
        model = ReceiptsIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ReceiptReadSerializer(serializers.ModelSerializer):
    ingredients = ReceiptsIngredientsReadSerializer(
                  
        many=True,
        source = 'ingredients_used'
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    class Meta:
        model = Receipts
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class ReceiptsM2MIngredients(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredients.objects.all())
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit', read_only=True)
    class Meta:
        model = ReceiptsIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ReceiptsM2MSTags(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tags.id', read_only=True)
    name = serializers.CharField(source='tags.name', read_only=True)
    color = serializers.CharField(source='tags.color', read_only=True)
    slug = serializers.CharField(source='tags.slug', read_only=True)
    class Meta:
        model = ReceiptsTags
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )

class ReceiptsCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = ReceiptsM2MIngredients(
        many=True,
        source='ingredients_used'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all(),
    )
    
    class Meta:
        model = Receipts
        fields = (
            'id',
            'ingredients',
            'tags',
            # 'image',
            'name',
            'text',
            'cooking_time'
        )
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        validated_data.update(author=author)
        receipt = Receipts.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredients = ingredient.get('ingredients')
            id = ingredients.get('id')
            amount = ingredient.get('amount')
            receipt.ingredients.add(id, through_defaults={'amount':amount})
        for tag in tags:
            receipt.tags.add(tag)
        return receipt
    
    def to_representation(self, instance):
        obj = super(ReceiptsCreateUpdateSerializer, self).to_representation(instance)
        ids = obj.get('tags')
        all_trags = []
        for id in ids:
            tag = Tags.objects.get(id=id)
            dict_tag = {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            }
            all_trags.append(dict_tag)            
        obj['tags'] = all_trags
        return obj
