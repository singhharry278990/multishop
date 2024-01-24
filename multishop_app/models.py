from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import *
from django.core.exceptions import ValidationError
import re

from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Spanish', 'Spanish'),
        ('Arabic', 'Arabic'),
        ('Chinese', 'Chinese'),
        ('Telugu', 'Telugu'),
        ('Urdu','Urdu'),
    ]


    ADDRESS_CATEGORY = (
        ('HOME', 'Home'),
        ('OFFICE', 'Office'),
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    phone_number = models.BigIntegerField(null=True)
    img = models.ImageField(upload_to='profile_pic/',default='profile_pic/default-profile-pic.webp')
    language = models.CharField(max_length=100,choices=LANGUAGE_CHOICES,default='English')
    apartment = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=100)
    address_category = models.CharField(choices=ADDRESS_CATEGORY, max_length=20)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Convert email to lowercase before saving
        super().save(*args, **kwargs)


    def __str__(self):
        return self.email


# Create your models here.
CATEGORY = (
    ('S', 'Shirt'),
    ('SP', 'Sport Wear'),
    ('OW', 'Out Wear')
)

LABEL = (
    ('N', 'New'),
    ('BS', 'Best Seller')
)

class Item(models.Model) :
    item_name = models.CharField(max_length=100)
    price = models.FloatField() 
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY, max_length=2)
    label = models.CharField(choices=LABEL, max_length=2)
    description = models.TextField()

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            "pk" : self.pk
        
        })

    def get_add_to_cart_url(self) :
        return reverse("core:add-to-cart", kwargs={
            "pk" : self.pk
        })

    def get_remove_from_cart_url(self) :
        return reverse("core:remove-from-cart", kwargs={
            "pk" : self.pk
        })
    
    

class OrderItem(models.Model) :
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.quantity} of {self.item.item_name}"
    
    

class Order(models.Model) :
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
