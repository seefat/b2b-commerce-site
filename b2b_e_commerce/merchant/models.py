from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.auth.models import AbstractUser
import uuid
from .status import ProductStatus, ConnectionStatus, PaymentOption
# from django.utils.text import slugify
from autoslug.fields import AutoSlugField

class BaseModel(models.Model):
    uid = models.UUIDField(unique=True,editable=False,default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True



class MerchantManager(BaseUserManager):
    def create_user(self, email, name, dob, password=None,**extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        if not name:
            raise ValueError('The Name field must be set.')
        if not dob:
            raise ValueError('The Date of Birth field must be set.')

        merchant = self.model(
            email=self.normalize_email(email),
            name=name,
            dob=dob,
            **extra_fields
        )
        merchant.set_password(password)
        merchant.save(using=self._db)
        return merchant

    def create_superuser(self, email, name, dob, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, name, dob, password, **extra_fields)


class Merchant(AbstractBaseUser, PermissionsMixin,BaseModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField(blank=True)

    # is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'dob']

    objects = MerchantManager()

    def __str__(self):
        return self.name



class Category(BaseModel):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='title',unique=True)


    def __str__(self):
        return f"UID: {self.uid}, Title: {self.title}"




class Shop(BaseModel):
    name = models.CharField(max_length=100, unique= True)
    slug = AutoSlugField(populate_from='name',unique=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    description = models.TextField()
    active = models.BooleanField(default=False) #should be changed
    connected_shops = models.ManyToManyField("self", through='ShopConnection', blank=True)
    def __str__(self):
        return self.name


class ShopConnection(BaseModel):
    sender_shop = models.ForeignKey(Shop, related_name='sent_connections', on_delete=models.CASCADE)
    receiver_shop = models.ForeignKey(Shop, related_name='received_connections', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ConnectionStatus.choices, default=ConnectionStatus.PENDING)

    def __str__(self):
        return f"Connection between {self.sender_shop} and {self.receiver_shop}"


class Product(BaseModel):
    title = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    slug =  AutoSlugField(populate_from='title')

    def __str__(self):
        return self.title


class Cart(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)


class CartItem(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    net_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)



class Order(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    # items = models.ForeignKey(CartItem, on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=150)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=20,choices=PaymentOption.choices)

class OrderItem(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    net_price = models.DecimalField(max_digits=8, decimal_places=2)