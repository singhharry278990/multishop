from django.urls import path
from .views import *
from .login import *
from .sign_up import *

urlpatterns = [
    path('', index, name='index'),
    path('details/', details, name='details'),
    path('cart/', cart, name='cart'),
    path('shop/', shop, name='shop'),
    path('checkout', checkout, name='checkout'),
    path('contact/', contact, name='contact'),
    path('contact_data/', contact, name='contact_data'),
    path('login/', login, name='login'),
    path('sign-up/', sign_up, name='sign-up'),
    path('login-api/', LoginView.as_view(), name='login-api'),
    path('address-post/', CustomerDetailView.as_view(), name='addeess-post'),
    path('token/', MyTokenObtainPairView.as_view(), name='token'),
    path('product/', ProductView.as_view(), name='get-product'),
    path('add-product/', AddProductView.as_view(), name='post-product'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token-refresh'),
    path('resgister/', ApiUserRegister.as_view(), name='resgister'),
    path('add-to-cart/<pk>/', AddToCartAndRemove.as_view(), name='add-to-cart'),
    path('remove-from-cart/<pk>/', AddToCartAndRemove.as_view(), name='remove-from-cart'),
    path('checkout/<id>/', CheckoutView.as_view(), name='checkout'),
    path('payment/', CreateCheckoutSession.as_view(), name='payment'),
    path('check-payment/', StripeWebhookView.as_view(), name='check-payment'),
]
