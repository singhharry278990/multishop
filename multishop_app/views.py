from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from rest_framework import status
from .models import *
from django.utils import timezone
from .serializer import *
import stripe, os

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class MyTokenRefreshView(TokenRefreshView):
    pass


class AddToCartAndRemove(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Item.objects.filter(pk=pk).first()
        except Item.DoesNotExist:
            raise serializers.ValidationError("Invalid item ID")
        
   
    def get_put_object(self, pk, user):

        try:
            item_obj = Item.objects.get(pk=pk)        
            try:
                order_item = OrderItem.objects.filter(user=user, item=item_obj).first()
                return order_item
            except OrderItem.DoesNotExist:
                raise serializers.ValidationError("Invalid item ID")
        except Item.DoesNotExist:
            raise serializers.ValidationError("Invalid item ID")


    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        item_data = self.get_object(kwargs.get('pk'))
        user = request.user
        if item_data is not None:
            serializer = AddToCartSerializer(data=request.data, context={'request': request, 'item_id': item_data.id})
            if serializer.is_valid():
                existing_order_item = self.get_put_object(pk, user)
                if existing_order_item:
                    serializer = AddToCartSerializer(instance=existing_order_item, data={'quantity': existing_order_item.quantity + 1}, partial=True)

                    if serializer.is_valid():
                        order_item = serializer.save()
                        response_data = {
                            'message': f'Item "{item_data.item_name}" quantity updated',
                            'quantity': order_item.quantity
                        }
                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                serializer.validated_data['user'] = user
                serializer.validated_data['item'] = item_data
                order_item = serializer.save()
                response_data = {
                    'message': f'Item "{item_data.item_name}" added to your cart',
                    'quantity': order_item.quantity
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": f"Item is not exist"}, status=status.HTTP_400_BAD_REQUEST)




    def put(self, request, *args, **kwargs):
        item_data = None
        pk = kwargs.get('pk')
        user = request.user
        item_data = self.get_put_object(pk, user)
        
        if item_data:
            serializer = PartiallyAddToCartSerializer(instance=item_data, data=request.data, context={'request': request}, partial=True)
            
            if serializer.is_valid():
                order_item = serializer.save()
                response_data = {
                    'message': f'Item "{order_item}" updated',
                    'quantity': order_item.quantity
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Item not found, create a cart'}, status=status.HTTP_404_NOT_FOUND)
        


    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        item_data = self.get_put_object(pk, user)
        if item_data:
            serializer = RemoveFromCartSerializer(instance=item_data)
            if serializer:
                serializer.delete()
                response_data = {
                            'message': f'Item "{item_data}" is removed from cart',
                        }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": f"Item {self.get_object(kwargs.get('pk'))} is already removed"}, status=status.HTTP_400_BAD_REQUEST)



class ProductView(APIView):

    def get(self, request):
        travel_queries = Item.objects.all()
        serializer = ProductSerializer(travel_queries, many=True)
        if serializer:
            return Response(serializer.data)
        else:
            return Response([])

class AddProductView(APIView):

    def post(self, request):
        response = {}
        serializer = AddProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response['message'] = "Created successfully"
            response['status'] = status.HTTP_200_OK
        else:
            response['message'] = "Validation error"
            response['errors'] = serializer.errors
            response['status'] = status.HTTP_400_BAD_REQUEST

        return Response(response)
    

    
class CustomerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {}
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            response['message'] = "created successfully"
            response['status'] = status.HTTP_200_OK
        else:
            response['message'] = "Something went wrong"
            response['errors'] = serializer.errors
            response['status'] = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response)   


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,id):
        response = {}
        # Retrieve the OrderItem object
        order_item = get_object_or_404(OrderItem, id=id, user=request.user, ordered=False)
        
        # Retrieve the Item object associated with the OrderItem
        item = get_object_or_404(Item, id=order_item.item_id, ordered=False)

        check_Address = Customer.objects.filter(user=request.user)

        if not check_Address.exists():
            response['message'] = "Validation error"
            response['errors'] = "Address Not Found"
            response['status'] = status.HTTP_404_NOT_FOUND
            return Response(response)


        address = get_object_or_404(Customer, user = request.user)
        response = {
            "User": request.user.username,
            "Item Name": item.item_name,
            "Quantity": order_item.quantity,
            "Actual Price": item.price,
            "Total Price": order_item.quantity * item.price,
            "Address":address.address +","+ address.city +","+ address.state +","+ address.pincode 
        }
       
        return Response(response)


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = {}
        dataDict = dict(request.data)
        price = int(dataDict['Total Price'])
        product_name = dataDict['Item Name']
        quantity = dataDict['Quantity']
        
        # Configure the Stripe API key
        stripe.api_key = os.environ.get('Secret_key')

        # Create a token for the card details
        token = 'tok_visa'  

        payment_intent_params = {
            'amount': price  * 100,
            'currency': 'inr',
            'payment_method_types': ['card'],
            'receipt_email': 'harsimran@snakescript.com',
            'description': product_name,
            'metadata': {
                'product_name': product_name,
                'quantity': quantity,
            },
            'payment_method_data': {
                'type': 'card',
                'card': {
                    'token': token,
                },
            },
            'confirm': True,
        }
    
        test_payment_intent = stripe.PaymentIntent.create(**payment_intent_params)

        if test_payment_intent.status == 'requires_action':
            response = {"response": test_payment_intent, "url": test_payment_intent.next_action.use_stripe_sdk.stripe_js}
            return Response(status=status.HTTP_200_OK, data=response)
        
        elif test_payment_intent.status == 'succeeded':
            updated_payment_intent = stripe.PaymentIntent.retrieve(test_payment_intent.id)
            return Response(status=status.HTTP_200_OK, data=updated_payment_intent)
        
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": "Payment processing failed."})



class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.data
        sig_header = "t=1492774577,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd,v0=6ffbb59b2300aae63f272406069a9788598b792a944a07aba816edb039989a39"
        
        endpoint_secret = 'whsec_c629bf77db5fd477d18b44265a2b13cd45d8d6bea5d8e496061beb8fb47a5f65'
        
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event based on its type
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object # contains a stripe.PaymentIntent
            print('PaymentIntent was successful!', payment_intent)
        elif event.type == 'payment_method.attached':
            payment_method = event.data.object # contains a stripe.PaymentMethod
            print('PaymentMethod was attached to a Customer!',payment_intent)
        # ... handle other event types
        else:
            print('Unhandled event type {}'.format(event.type))
        
        return Response(status=status.HTTP_200_OK)

def index(request):
    return render(request, 'index.html')

def details(request):
    return render(request, 'details.html')

def checkout(request):
    return render(request, 'checkout.html')

def contact(request):
    return render(request, 'contact.html')

def shop(request):
    return render(request, 'shop.html')

def cart(request):
    return render(request, 'cart.html')

def login(request):
    return render(request, 'login.html')

def sign_up(request):
    return render(request, 'sign-up.html')


def contact_data(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Process the data and send the email

        # Return a success JSON response
        return JsonResponse({'message': 'Your message has been sent.'})

    # Return an error JSON response if the request is not POST
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
