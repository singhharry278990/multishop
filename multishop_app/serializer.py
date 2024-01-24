from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *
import logging

logger = logging.getLogger(__name__)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                msg = 'Access denied: wrong email or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "email" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_name', 'price','discount_price', 'category', 'label', 'description']



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'address', 'phone', 'state', 'email', 'city', 'pincode', 'address_category']
    
    def validate(self, attrs):
        if not attrs['name']:
            raise serializers.ValidationError("Please enter your Name!")
        elif len(attrs['name']) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        elif not attrs['phone']:
            raise serializers.ValidationError("Please enter your Phone Number!")
        elif len(attrs['phone']) < 10:
            raise serializers.ValidationError("Phone Number must be 10 characters long.")
        elif len(attrs['email']) < 5:
            raise serializers.ValidationError("Email must be at least 5 characters long.")
        elif len(attrs['pincode']) < 6:
            raise serializers.ValidationError("Pincode must be 6 characters long.")
        return attrs

    def create(self, validated_data):
        customer = CustomUser.objects.create(**validated_data)
        customer.save()
        return customer



class AddProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_name', 'price', 'discount_price', 'category', 'label', 'description']

    def validate(self, attrs):
        if not attrs.get('item_name'):
            raise serializers.ValidationError("Please enter Item Name!")
        elif not attrs.get('price'):
            raise serializers.ValidationError("Please enter Item Price!")
        elif not attrs.get('discount_price'):
            raise serializers.ValidationError("Please enter Discount Price!")
        elif not attrs.get('category'):
            raise serializers.ValidationError("Please enter Category.")
        elif not attrs.get('label'):
            raise serializers.ValidationError("Please enter Label!")
        elif not attrs.get('description') or len(attrs['description']) < 10:
            raise serializers.ValidationError("Please enter Item Description (at least 10 characters)!")
        return attrs

    def create(self, validated_data):
        product = Item.objects.create(**validated_data)
        return product

class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_name', 'price', 'discount_price', 'category', 'label', 'description']

    def validate(self, attrs):
        if not attrs.get('item_name'):
            raise serializers.ValidationError("Please enter Item Name!")
        elif not attrs.get('price'):
            raise serializers.ValidationError("Please enter Item Price!")
        elif not attrs.get('discount_price'):
            raise serializers.ValidationError("Please enter Discount Price!")
        elif not attrs.get('category'):
            raise serializers.ValidationError("Please enter Category.")
        elif not attrs.get('label'):
            raise serializers.ValidationError("Please enter Label!")
        elif not attrs.get('description') or len(attrs['description']) < 10:
            raise serializers.ValidationError("Please enter Item Description (at least 10 characters)!")
        return attrs





class AddToCartSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, default=1)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = OrderItem
        fields = '__all__'

    def validate_item_id(self, item_id):
        item_id = self.context.get('item_id')
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Invalid item ID")

        return item


    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        user = self.context['request'].user

        existing_order_item = OrderItem.objects.filter(user=user, item=item).first()
        if existing_order_item:

            existing_order_item.quantity += quantity
            existing_order_item.save()
            return existing_order_item
        
        item_obj = OrderItem.objects.create(user=user, item=item, quantity=quantity)
        item_obj.save()
        return item_obj





class PartiallyAddToCartSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, default=1)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = OrderItem
        fields = '__all__'

    def update(self, instance, validated_data):
        # Increment the quantity by 1
        instance.quantity += 1
        instance.save()
        return instance


class ItemSerializer(serializers.ModelSerializer):
     class Meta:
         model = Item
         fields = "__all__"



class RemoveFromCartSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    def validate_item_id(self, item_id):
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Invalid item ID")

        return item

    class Meta:
        model = OrderItem
        fields = '__all__'

    def delete(self):
        self.instance.delete()