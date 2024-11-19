from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
import logging
logger = logging.getLogger(__name__) 
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny   
from django.contrib.auth import get_user_model

user_model = get_user_model()
import csv
 
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile   
 
 
 


class UserTypeListCreateView(generics.ListCreateAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer



class UserTypeListView(generics.ListAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

    def list(self, request, *args, **kwargs):
        # Call the superclass method to get the response
        response = super().list(request, *args, **kwargs)
        
 
        print("Response Data:", response.data)   
        
        # Return the response
        return response
 
class UserTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer
    
class CategoryCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve categories and order by ID
        categories = Category.objects.all().order_by('id')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            return None

    def get(self, request, id, *args, **kwargs):
        category = self.get_object(id)
        if category is None:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, id, *args, **kwargs):
        print("request.data", request.data)
        category = self.get_object(id)
        if category is None:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, *args, **kwargs):
        category = self.get_object(id)
        if category is None:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    
    
    
 



class ProductListCreateView(APIView):
    def post(self, request):
        print("Request Data:", request.data)

       
        if Product.objects.filter(SKU=request.data.get('SKU').strip()).exists():
            return Response({"error": "Product with this SKU already exists."}, status=status.HTTP_400_BAD_REQUEST)

        usertypes = request.data.getlist('usertypes')
        cleaned_usertypes = [int(u) for u in usertypes if u.isdigit()]

        usertype_instances = UserType.objects.filter(id__in=cleaned_usertypes)
        if len(usertype_instances) != len(cleaned_usertypes):
            raise ValidationError("One or more user types do not exist.")

        cleaned_data = {
            'SKU': request.data.get('SKU').strip(),  
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
            'color': request.data.get('color'),
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
            'product_size': request.data.get('product_size'),
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
            'product_image': request.FILES.get('product_image'),
        }

        serializer = ProductSerializer(data=cleaned_data)

        if serializer.is_valid():
            product = serializer.save()

        
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                ProductMultipleImages.objects.create(product=product, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
 
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
      
        return Response(serializer.data, status=status.HTTP_200_OK)
 

from rest_framework.permissions import IsAuthenticated
class ProductuserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
  
        current_user_usertype = request.user.usertypes

  
        print("Current User's UserType:", current_user_usertype)

   
        products = Product.objects.filter(usertypes=current_user_usertype)

    
        print("Fetched Products:", products)

       
        serializer = ProductSerializer(products, many=True)

   
        print("Serialized Product Data:", serializer.data)

    
        return Response(serializer.data)

 
class ProductUpdateView(APIView):
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Debugging the incoming request data and files
        print("Request Data:", request.data)
        print("Request Files:", request.FILES)

        # Handle usertypes data
        usertypes = request.data.get('usertypes', '').split(',')
        cleaned_usertypes = [int(u.strip()) for u in usertypes if u.strip().isdigit()]

        # Extract the cleaned data for the product
        cleaned_data = {
            'SKU': request.data.get('SKU'),
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
            'color': request.data.get('color'),
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
            'product_size': request.data.get('product_size'),
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
        }

        # Handle main product image
        product_image = request.FILES.get('product_image')
        if product_image:
            cleaned_data['product_image'] = product_image

        # Handle additional images
        additional_images = request.FILES.getlist('additional_images')
        print("Additional Images Received:", additional_images)

        # Images to remove (if specified by the user)
        images_to_remove = request.data.getlist('images_to_remove[]')
        print("Images to Remove:", images_to_remove)

        # Updating the product data
        serializer = ProductSerializer(product, data=cleaned_data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

            # Remove images the user requested to delete
            if images_to_remove:
                ProductMultipleImages.objects.filter(id__in=images_to_remove, product=product).delete()

            # Add any new images provided in the request
            for image in additional_images:
                ProductMultipleImages.objects.create(product=product, image=image)

            # Fetch the updated product with images
            updated_product = Product.objects.prefetch_related('additional_images').get(pk=product.pk)
            updated_serializer = ProductSerializer(updated_product)

            print("Product updated successfully:", updated_serializer.data)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        # Handle serialization errors
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductDeleteView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

    def delete(self, request, id, *args, **kwargs):
        product = self.get_object(id)
        if product is None:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
 
        if product.product_image:
            product.product_image.delete(save=False)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #***************************************************************************************************************************************
    
    
    
class CustomizedProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomizedProduct.objects.all()
    serializer_class = CustomizedProductListSerializer
    
    
    
 

 

class CustomizedProductListCreateView(APIView):
    def post(self, request):
        print("Request Data:", request.data)

       
        if CustomizedProduct.objects.filter(SKU=request.data.get('SKU').strip()).exists():
            return Response({"error": "Product with this SKU already exists."}, status=status.HTTP_400_BAD_REQUEST)

        usertypes = request.data.getlist('usertypes')
        cleaned_usertypes = [int(u) for u in usertypes if u.isdigit()]

        usertype_instances = UserType.objects.filter(id__in=cleaned_usertypes)
        if len(usertype_instances) != len(cleaned_usertypes):
            raise ValidationError("One or more user types do not exist.")

        cleaned_data = {
            'SKU': request.data.get('SKU').strip(),  
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
           
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
            'product_size': request.data.get('product_size'),
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
            'product_image': request.FILES.get('product_image'),
        }

        serializer = CustomizedProductSerializer(data=cleaned_data)

        if serializer.is_valid():
            product = serializer.save()

        
            additional_images = request.FILES.getlist('additional_images')
            for image in additional_images:
                CustomizedProductMultipleImages.objects.create(product=product, image=image)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
 
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomizedProductListView(APIView):
    def get(self, request):
        products = CustomizedProduct.objects.all()
        serializer = CustomizedProductListSerializer(products, many=True)
        print("serializer.data",serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
 

class CustomProductuserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
  
        current_user_usertype = request.user.usertypes

  
        print("Current User's UserType:", current_user_usertype)

   
        products = CustomizedProduct.objects.filter(usertypes=current_user_usertype)

    
        print("Fetched Products:", products)

       
        serializer = CustomizedProductSerializer(products, many=True)

   
        print("Serialized Product Data:", serializer.data)

    
        return Response(serializer.data)

 
class CustomizedProductUpdateView(APIView):
    def put(self, request, pk):
        try:
            product = CustomizedProduct.objects.get(pk=pk)
        except CustomizedProduct.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Debugging the incoming request data and files
        print("Request Data:", request.data)
        print("Request Files:", request.FILES)

        # Handle usertypes data
        usertypes = request.data.get('usertypes', '').split(',')
        cleaned_usertypes = [int(u.strip()) for u in usertypes if u.strip().isdigit()]

        # Extract the cleaned data for the product
        cleaned_data = {
            'SKU': request.data.get('SKU'),
            'product_name': request.data.get('product_name'),
            'category': request.data.get('category'),
           
            'gross_weight': request.data.get('gross_weight'),
            'diamond_weight': request.data.get('diamond_weight'),
            'colour_stones': request.data.get('colour_stones'),
            'net_weight': request.data.get('net_weight'),
            'product_size': request.data.get('product_size'),
            'description': request.data.get('description'),
            'usertypes': cleaned_usertypes,
        }

        # Handle main product image
        product_image = request.FILES.get('product_image')
        if product_image:
            cleaned_data['product_image'] = product_image

        # Handle additional images
        additional_images = request.FILES.getlist('additional_images')
        print("Additional Images Received:", additional_images)

        # Images to remove (if specified by the user)
        images_to_remove = request.data.getlist('images_to_remove[]')
        print("Images to Remove:", images_to_remove)

        # Updating the product data
        serializer = CustomizedProductSerializer(product, data=cleaned_data, partial=True)
        if serializer.is_valid():
            product = serializer.save()

            # Remove images the user requested to delete
            if images_to_remove:
                CustomizedProductMultipleImages.objects.filter(id__in=images_to_remove, product=product).delete()

            # Add any new images provided in the request
            for image in additional_images:
                CustomizedProductMultipleImages.objects.create(product=product, image=image)

            # Fetch the updated product with images
            updated_product = CustomizedProduct.objects.prefetch_related('additional_images').get(pk=product.pk)
            updated_serializer = CustomizedProductSerializer(updated_product)

            print("Product updated successfully:", updated_serializer.data)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        # Handle serialization errors
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomizedProductDeleteView(APIView):

    def get_object(self, id):
        try:
            return CustomizedProduct.objects.get(id=id)
        except CustomizedProduct.DoesNotExist:
            return None

    def delete(self, request, id, *args, **kwargs):
        product = self.get_object(id)
        if product is None:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
 
        if product.product_image:
            product.product_image.delete(save=False)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    




class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
  

    def create(self, request, *args, **kwargs):
        print("Incoming Data:", request.data)
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)   
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print("Before Saving User")
        self.perform_create(serializer)
        print("Created User Data:", serializer.data)   
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()   
        print("Queryset:", users)   
        
        serializer = self.get_serializer(users, many=True)
        print("serializer.data",serializer.data)
        return Response(serializer.data)  
    

   
 

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'id'

    def get_object(self):
        # Get the user to be updated based on the ID in the URL
        return super().get_object()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Print the incoming request data for debugging
        print("Incoming Request Data:", request.data)

        # Create a serializer instance with the provided data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        # Validate and update the user data
        if serializer.is_valid():
            self.perform_update(serializer)
            print("Updated User Data:", serializer.data)  # Print updated user data
            return Response(serializer.data)

        # Print serializer errors for debugging
        print("Update Errors:", serializer.errors)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer  

    def delete(self, request, *args, **kwargs):
        user = self.get_object()  
        user.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)
    

 



class AdminLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        logger.info(f"Attempting to login user with email: {email}")

        if email is None or password is None:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        logger.warning(f"Failed login attempt for user: {email}")
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


 
 

class ChangePasswordView(APIView):
    def put(self, request, *args, **kwargs):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Both new password and confirm password must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'},
                            status=status.HTTP_400_BAD_REQUEST)

      
        admin_users = User.objects.filter(is_staff=True, is_superuser=True)

        if not admin_users.exists():
            return Response({'error': 'No admin users found.'},
                            status=status.HTTP_404_NOT_FOUND)

       
        for admin_user in admin_users:
        
            print(f"Admin User Data:")
            print(f"Email: {admin_user.email}")
            print(f"Full Name: {admin_user.full_name}")
            print(f"Mobile Number: {admin_user.mobile_number}")
            print(f"Is Staff: {admin_user.is_staff}")
            print(f"Is Superuser: {admin_user.is_superuser}")
            print(f"User ID: {admin_user.id}")

         
            admin_user.set_password(new_password)
            admin_user.save()

        return Response({'message': 'Password changed successfully for all admin users.'},
                        status=status.HTTP_200_OK)



class MediaUploadView(APIView):
    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')  
        media_objects = []

        for image in images:
            media_instance = Media(image=image)  
            media_instance.save() 
            media_objects.append(media_instance)

        serializer = MediaSerializer(media_objects, many=True)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

 
import re
import os
import csv
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Product, Category, Media, UserType

import re
import os
import csv
import logging
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Product, Category, Media, UserType

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # You can change this to INFO or ERROR depending on your needs
handler = logging.StreamHandler()  # Logs to console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

import re
import os
import csv
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Product, Category, Media, UserType
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ProductCSVUploadView(APIView):
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')

        if not csv_file:
            logger.error("No file uploaded.")
            return Response({"error": "No file uploaded. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        # Log the file name and size to ensure it is received correctly
        logger.info(f"Uploaded file: {csv_file.name}, size: {csv_file.size} bytes")

        # Save the file temporarily
        file_path = default_storage.save(f'tmp/{csv_file.name}', ContentFile(csv_file.read()))
        logger.info(f"File saved temporarily at {file_path}")

        try:
            with default_storage.open(file_path) as file:
                decoded_file = file.read().decode('utf-8').splitlines()
                logger.debug(f"Decoded file content: {decoded_file[:200]}")  # Log the first 200 characters of the CSV for verification
                reader = csv.DictReader(decoded_file)

                expected_headers = {
                    'SKU', 'product_name', 'category',
                    'gross_weight', 'diamond_weight', 'colour_stones',
                    'net_weight', 'product_size', 'product_image',
                    'usertypes'
                }

                detected_headers = set(reader.fieldnames or [])
                logger.info(f"Expected headers: {expected_headers}")
                logger.info(f"Detected headers: {detected_headers}")

                if not expected_headers.issubset(detected_headers):
                    missing_headers = expected_headers - detected_headers
                    logger.error(f"CSV file is missing required headers: {missing_headers}")
                    return Response({"error": f"CSV file is missing required headers: {missing_headers}"}, status=status.HTTP_400_BAD_REQUEST)

                for row in reader:
                    try:
                        required_fields = ['SKU', 'product_name', 'category', 'gross_weight', 'net_weight', 'product_size']
                        for field in required_fields:
                            if not row.get(field):
                                raise ValueError(f"Field '{field}' is required but missing or empty in the row.")

                        if Product.objects.filter(SKU=row['SKU']).exists():
                            logger.warning(f"Product with SKU {row['SKU']} already exists.")
                            continue  

                        category_name = row['category']
                        category, _ = Category.objects.get_or_create(category_name=category_name)

                        product = Product.objects.create(
                            SKU=row['SKU'],
                            product_name=row['product_name'],
                            category=category,
                            gross_weight=row['gross_weight'],
                            diamond_weight=row.get('diamond_weight', 0),
                            colour_stones=row.get('colour_stones', ''),
                            net_weight=row['net_weight'],
                            product_size=row['product_size'],
                        )
                        logger.info(f"Product with SKU {row['SKU']} created successfully.")

                        if row.get('usertypes'):
                            usertypes_list = [ut.strip() for ut in row['usertypes'].split(',')]
                            for usertype_name in usertypes_list:
                                usertype, _ = UserType.objects.get_or_create(usertype=usertype_name)
                                product.usertypes.add(usertype)

                        sku = row['SKU']
                        sku_prefix = sku.replace(" ", "_")

                        try:
                            media_image = Media.objects.filter(image__icontains=sku_prefix).first()
                            if media_image:
                                original_image_name = media_image.image.name
                                cleaned_image_name = re.sub(r'_[^_]+\.', '.', original_image_name)

                                product.product_image = cleaned_image_name
                                product.save()
                                logger.info(f"Image {cleaned_image_name} assigned to product {sku}.")
                            else:
                                product.product_image = 'products/default_image.jpg'
                                product.save()
                                logger.warning(f"No image found for SKU {sku}. Assigning default image.")
                        except Exception as e:
                            logger.error(f"Error while searching for image for SKU {sku}: {e}")
                            logger.exception("Exception details:")

                        logger.info(f"Successfully processed SKU: {sku}")

                    except ValueError as ve:
                        logger.error(f"Validation error for row with SKU {row.get('SKU', 'unknown')}: {ve}")
                        logger.exception("Exception details:")  # Logs the full stack trace
                        continue  
                    except Exception as e:
                        logger.error(f"Unexpected error for row with SKU {row.get('SKU', 'unknown')}: {e}")
                        logger.exception("Exception details:")  # Logs the full stack trace
                        continue   

            return Response({"message": "Products uploaded successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            logger.exception("Exception details:")
            return Response({"error": "Failed to process the uploaded file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class MediaListView(APIView):
    def get(self, request, *args, **kwargs):
        media_images = Media.objects.all()
        serializer = MediaSerializer(media_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class MediaDeleteView(APIView):   
    def delete(self, request, pk):
        try:
            media = Media.objects.get(pk=pk)  
            media.delete()  
            return Response({'message': 'Media deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Media.DoesNotExist:
            return Response({'error': 'Media not found'}, status=status.HTTP_404_NOT_FOUND)
        
class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user =user_model.objects.get(email=email)
           
            refresh = RefreshToken.for_user(user)  
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


class ProductDetailView(APIView):
    def get(self, request, pk):  
        try:
            product = Product.objects.get(id=pk)   
            serializer = ProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
 


 

class ProductSKUDetailView(APIView):
    def get(self, request, SKU): 
        try:
            product = Product.objects.get(SKU=SKU)   
            serializer = ProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.permissions import IsAuthenticated
 

 
class AddToCartView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        color = request.data.get('color')  # Retrieve color from request

        if not color:
            return Response({'detail': 'Please select a color!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            existing_item = self.queryset.get(product_id=product_id, user=request.user)

            # Increment quantity
            existing_item.quantity += quantity

            # Fetch the product again to recalculate weights
            product = Product.objects.get(id=product_id)

            # Recalculate weights based on new quantity
            existing_item.gross_weight = product.gross_weight * existing_item.quantity
            existing_item.diamond_weight = (product.diamond_weight or 0) * existing_item.quantity
            existing_item.colour_stones = product.colour_stones * existing_item.quantity
            existing_item.net_weight = product.net_weight * existing_item.quantity
            existing_item.color = color  # Update color in cart

            existing_item.save()

            serializer = self.get_serializer(existing_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, color=color)  # Include color when creating a new cart item
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
    
class CartItemsView(generics.ListAPIView):
    serializer_class = CartGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # print("serializer.datassssssssssssssssss:", serializer.data)   
        return Response(serializer.data)

    

    
class CartItemDeleteAPIView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
       
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        sku = self.kwargs.get("sku")
  
        cart_items = self.get_queryset().filter(product__SKU=sku)

        if not cart_items.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)  # 
        
      
        deleted_count, _ = cart_items.delete()
        
        if deleted_count == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)  

        return Response(status=status.HTTP_204_NO_CONTENT)


 
 
 

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order, Cart
from .serializers import OrderSerializer

from django.core.mail import send_mail
from django.conf import settings

class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Create the order and associate it with the logged-in user
        order = serializer.save(user=self.request.user)

        # Clear the cart after order creation
        Cart.objects.filter(user=self.request.user).delete()     

        # Send email to the admin
        self.send_order_confirmation_email(order)

        return order 

    def send_order_confirmation_email(self, order):
        # Create the email content
        subject = f"New Order Created: {order.id}"
        message = f"Order ID: {order.id}\n" \
                  f"User: {order.user.username}\n" \
                  f"Total Gross Weight: {order.total_gross_weight}\n" \
                  f"Total Diamond Weight: {order.total_diamond_weight}\n" \
                  f"Total Colour Stones: {order.total_colour_stones}\n" \
                  f"Total Net Weight: {order.total_net_weight}\n" \
                  f"Created At: {order.created_at}\n" \
                  f"Order Items: \n"
        
        for item in order.order_items.all():
            message += f"- {item.product.product_name} (Quantity: {item.quantity})\n"

        # Send the email to the admin
        admin_email = "admin@example.com"  # Replace with the actual admin email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender's email
            [admin_email],  # Recipient's email
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = self.perform_create(serializer)
        order_data = {
            "id": order.id,
            "user": order.user.username,
            "total_gross_weight": str(order.total_gross_weight),
            "total_diamond_weight": str(order.total_diamond_weight),
            "total_colour_stones": str(order.total_colour_stones),
            "total_net_weight": str(order.total_net_weight),
            "created_at": order.created_at.isoformat(),
            "order_items": [
                {
                    "product": item.product.product_name,
                    "quantity": item.quantity,
                    "color":item.color,
                    "additional_notes": item.additional_notes,
                } for item in order.order_items.all()
            ]
        }
        
        print("Created order data:", order_data)
        return Response(order_data, status=status.HTTP_201_CREATED)



# class OrderCreateView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         order = serializer.save(user=self.request.user)
#         Cart.objects.filter(user=self.request.user).delete()     
#         return order 

#     def create(self, request, *args, **kwargs):
#         print("Incoming request data:", request.data)
#         serializer = self.get_serializer(data=request.data)

#         if not serializer.is_valid():
#             print("Validation errors:", serializer.errors)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         order = self.perform_create(serializer)
#         order_data = {
#             "id": order.id,
#             "user": order.user.username,
#             "total_gross_weight": str(order.total_gross_weight),
#             "total_diamond_weight": str(order.total_diamond_weight),
#             "total_colour_stones": str(order.total_colour_stones),
#             "total_net_weight": str(order.total_net_weight),
#             "created_at": order.created_at.isoformat(),
#             "order_items": [
#                 {
#                     "product": item.product.product_name,
#                     "quantity": item.quantity,
#                     "additional_notes": item.additional_notes,
#                 } for item in order.order_items.all()
#             ]
#         }
        
#         print("Created order data:", order_data)
#         return Response(order_data, status=status.HTTP_201_CREATED)




# from twilio.rest import Client
# from django.conf import settings

# from twilio.rest import Client
# from django.conf import settings
# from rest_framework import generics, status
# from rest_framework.response import Response
# from .models import Order, Cart
# from .serializers import OrderSerializer
# from rest_framework import permissions

# class OrderCreateView(generics.CreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         # Save the order and associate it with the user
#         order = serializer.save(user=self.request.user)
        
#         # Assuming you have a Cart model related to the user
#         # Clear the user's cart items after order creation
#         Cart.objects.filter(user=self.request.user).delete()
        
#         return order

#     def create(self, request, *args, **kwargs):
#         print("Incoming request data:", request.data)
#         serializer = self.get_serializer(data=request.data)

#         if not serializer.is_valid():
#             print("Validation errors:", serializer.errors)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         order = self.perform_create(serializer)

#         # Prepare order data to include in the response
#         order_data = {
#             "id": order.id,
#             "user": order.user.username,
#             "total_gross_weight": str(order.total_gross_weight),
#             "total_diamond_weight": str(order.total_diamond_weight),
#             "total_colour_stones": str(order.total_colour_stones),
#             "total_net_weight": str(order.total_net_weight),
#             "created_at": order.created_at.isoformat(),
#             "order_items": [
#                 {
#                     "product": item.product.product_name,
#                     "quantity": item.quantity,
#                     "additional_notes": item.additional_notes,
#                 } for item in order.order_items.all()
#             ]
#         }
        
#         print("Created order data:", order_data)

#         # Send WhatsApp message to the user
#         try:
#             # Twilio client setup
#             client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

#             # User's WhatsApp number (replace with the actual field where you store it)
#             user_whatsapp_number = f"whatsapp:+{self.request.user.whatsapp_number}"

#             # Message content
#             message_body = (
#                 f"Hello {self.request.user.username},\n"
#                 f"Thank you for your order!\n\nOrder Details:\n"
#                 f"Order ID: {order.id}\n"
#                 f"Total Gross Weight: {order.total_gross_weight}g\n"
#                 f"Total Diamond Weight: {order.total_diamond_weight} carats\n"
#                 f"Total Net Weight: {order.total_net_weight}g\n\n"
#                 f"We appreciate your business!"
#             )

#             # Send message
#             client.messages.create(
#                 body=message_body,
#                 from_=settings.TWILIO_WHATSAPP_NUMBER,
#                 to=user_whatsapp_number
#             )

#             print(f"WhatsApp message sent to {user_whatsapp_number}")

#         except Exception as e:
#             print(f"Failed to send WhatsApp message: {e}")

#         return Response(order_data, status=status.HTTP_201_CREATED)




class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  
        serializer = UserGetSerializer(user)   
        return Response(serializer.data)
    
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer 
    update_serializer_class = UserGetSerializer   
    permission_classes = [IsAuthenticated]  

    def get_object(self):
   
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.update_serializer_class(self.object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

 

from urllib.parse import unquote

class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, sku):
        sku = unquote(sku)  # Ensure SKU is decoded
        user = request.user
        quantity = request.data.get('quantity')
        color = request.data.get('color')

        print("Decoded SKU:", sku)
        print("Quantity:", quantity)
        print("Color:", color)

        if quantity is None or quantity < 1:
            print("Invalid quantity or missing quantity")
            return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = Cart.objects.get(user=user, product__SKU=sku)
            print("Found cart item:", cart_item)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_item.quantity = quantity
        cart_item.color = color
        cart_item.gross_weight = cart_item.product.gross_weight * quantity
        cart_item.diamond_weight = (cart_item.product.diamond_weight or 0) * quantity
        cart_item.colour_stones = cart_item.product.colour_stones * quantity
        cart_item.net_weight = cart_item.product.net_weight * quantity
        cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)




from django.db.models import Sum   
class CartItemListView(generics.ListAPIView):
    serializer_class = CartGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_carts = Cart.objects.filter(user=self.request.user)

      
        total_weights = user_carts.aggregate(
            total_gross_weight=Sum('gross_weight'),
            total_diamond_weight=Sum('diamond_weight'),
            total_colour_stones=Sum('colour_stones'),
            total_net_weight=Sum('net_weight')
        )

        return {
            'cart_items': user_carts,
            'totals': total_weights
        }

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        cart_items = queryset['cart_items']
        totals = queryset['totals']
        
        
        serializer = self.get_serializer(cart_items, many=True)

        return Response({
            'cart_items': serializer.data,
            'totals': totals
        })
        
class UserOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializerss

    def get_queryset(self):
        user_orders = Order.objects.filter(user=self.request.user)
        
        
        for order in user_orders:
            print(f"Order ID: {order.id}, Total Gross Weight: {order.total_gross_weight}, "
                  f"Total Diamond Weight: {order.total_diamond_weight}, "
                  f"Total Color Stones: {order.total_colour_stones}, "
                  f"Total Net Weight: {order.total_net_weight}")
        
        return user_orders
    
class CustomizedProductDetail(generics.RetrieveAPIView):
    queryset = CustomizedProduct.objects.all()
    serializer_class = CustomizedProductListSerializer

class CustomizedProductSKUDetailView(APIView):
    def get(self, request, SKU): 
        try:
            product = CustomizedProduct.objects.get(SKU=SKU)   
            serializer =CustomizedProductListSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


 
 

class CustomizedOrderCreateView(generics.CreateAPIView):
    queryset = CustomizedOrder.objects.all()
    serializer_class = CustomizedOrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
   
        order = serializer.save(user=self.request.user)

       
        self.send_order_confirmation_email(order)

        return order

    def send_order_confirmation_email(self, order):
 
        subject = f"New Customized Order Created: {order.id}"
        message = (
            f"Order ID: {order.id}\n"
            f"User: {order.user.username}\n"
            f"Product: {order.product.product_name}\n"
            f"Size: {order.size}\n"
            f"Gram: {order.gram}\n"
            f"Cent: {order.cent}\n"
            f"Color: {order.color.color}\n"
            f"Description: {order.description}\n"
            f"Quantity: {order.quantity}\n"
            f"Status: {order.status}\n"
            f"New Status: {order.new_status}\n"
            f"Due Date: {localtime(order.due_date).strftime('%Y-%m-%d %H:%M:%S') if order.due_date else 'N/A'}\n"
            f"Created At: {localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    
        admin_email = "admin@example.com"   
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  
            [admin_email],  
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        print("Received data:", request.data)
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            order = self.perform_create(serializer)  # Ensure the order is created
            headers = self.get_success_headers(serializer.data)
            print("serializer.data", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print("Validation Error:", e)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ColorListCreate(generics.ListCreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class ColorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorupdateSerializer
    
class ColorListView(generics.ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    
    
 

 

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils.timezone import localtime
from .models import FullCustomizedOrder, FullCustomizedMultipleImages, Category, Color
from .serializers import FullCustomizedOrderSerializer
from django.conf import settings
from django.contrib.auth.models import User

class FullCustomizedOrderCreateView(generics.CreateAPIView):
    queryset = FullCustomizedOrder.objects.all()
    serializer_class = FullCustomizedOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Create the order and associate it with the logged-in user
        order = serializer.save(user=self.request.user)

        # Handle additional images
        files = self.request.FILES.getlist('product_images')
        for file in files:
            FullCustomizedMultipleImages.objects.create(product_images=order, image=file)

        # Send email to admin after order creation
        self.send_order_confirmation_email(order)

        return order

    def send_order_confirmation_email(self, order):
        # Create the email content
        subject = f"New Full Customized Order Created: {order.id}"
        message = (
            f"Order ID: {order.id}\n"
            f"User: {order.user.username}\n"
            f"Category: {order.category.category_name}\n"  # Adjusted for actual field name in Category model
            f"Design Number: {order.design_number}\n"
            f"Size: {order.size}\n"
            f"Gram: {order.gram}\n"
            f"Cent: {order.cent}\n"
            f"Color: {order.color.color}\n"
            f"Description: {order.description}\n"
            f"Quantity: {order.quantity}\n"
            f"Status: {order.status}\n"
            f"New Status: {order.new_status}\n"
            f"Due Date: {localtime(order.due_date).strftime('%Y-%m-%d %H:%M:%S') if order.due_date else 'N/A'}\n"
            f"Created At: {localtime(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Order Images: \n"
        )

        # Include the URLs of the images associated with the order
        for image in FullCustomizedMultipleImages.objects.filter(product_images=order):
            message += f"- {image.image.url}\n"  # Add image URLs

        # Send the email to the admin
        admin_email = "admin@example.com"  # Replace with the actual admin email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender's email (configured in settings)
            [admin_email],  # Admin's email
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = self.perform_create(serializer)
        order_data = {
            "id": order.id,
            "user": order.user.username,
            "design_number": order.design_number,
            "size": order.size,
            "gram": str(order.gram),
            "cent": str(order.cent),
            "color": order.color.color,  # Ensure correct field for color
            "description": order.description,
            "quantity": order.quantity,
            "status": order.status,
            "new_status": order.new_status,
            "due_date": order.due_date.isoformat() if order.due_date else None,
            "created_at": order.created_at.isoformat(),
            "order_images": [image.image.url for image in FullCustomizedMultipleImages.objects.filter(product_images=order)]
        }

        print("Created order data:", order_data)
        return Response(order_data, status=status.HTTP_201_CREATED)



    
class UserCartItemCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
 
        cart_item_count = Cart.objects.filter(user=request.user).count()
        return Response({'cart_item_count': cart_item_count})
    
class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializerss
 
class OrderUpdateAPIView(APIView):
    def patch(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderIdSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderUpdateAPIView(APIView):
    def patch(self, request, pk):
  
        order = Order.objects.filter(pk=pk).first()
        
        if not order:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        print("Received data:", request.data)   
        
   
        ordercode = request.data.get('ordercode', order.ordercode)
        order.ordercode = ordercode
        order.save()   

    
        order_items_data = request.data.get('order_items', [])
        for item_data in order_items_data:
            print("Processing item data:", item_data)

            item_id = item_data.get('id') 
            if item_id is not None:   
       
                item = OrderItem.objects.filter(pk=item_id).first()
                
                if item:
                
                    quantity = int(item_data.get('quantity', item.quantity))
                    item.quantity = quantity
                    item.save()   
                else:
                    print("No ID found in item data:", item_data)
                    return Response({"detail": f"OrderItem with id {item_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({'ordercode': order.ordercode, 'order_items': order_items_data}, status=status.HTTP_200_OK)


class DeleteOrderView(APIView):
    def delete(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return Response({"message": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
 


class PendingOrdersView(APIView):
    def get(self, request):
        pending_orders = CustomizedOrder.objects.filter(status='pending')
        serializer = CustomizedOrderSerializer(pending_orders, many=True)
        return Response(serializer.data)
    
class OrderApprovalView(APIView):
    def patch(self, request, pk):
        try:
            order = CustomizedOrder.objects.get(pk=pk)
        except CustomizedOrder.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        approved = request.data.get("approved")
        
        if approved is not None:
            # Update status based on approved value
            order.status = 'approved' if approved else 'rejected'
            order.save()
            return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)
class RejectOrderAPIView(APIView):
    def patch(self, request, pk):
        try:
            order = CustomizedOrder.objects.get(pk=pk)
        except CustomizedOrder.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Set the status to 'rejected'
        order.status = 'rejected'
        order.save()

        serializer = CustomizedOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class  ApprovedOrdersView(APIView):
    def get(self, request):
        pending_orders = CustomizedOrder.objects.filter(status='approved')
        serializer = CustomizedOrderSerializer(pending_orders, many=True)
        return Response(serializer.data)
    
    
from datetime import timedelta
from django.utils import timezone
 
class GenerateOrderIDView(APIView):
    def patch(self, request, pk=None):
        order = get_object_or_404(CustomizedOrder, pk=pk)
        ordercode = request.data.get('ordercode')
        due_date = request.data.get('due_date')   

        if ordercode:
            order.ordercode = ordercode

    
            if due_date:
                order.due_date = due_date
            else:
                 
                order.due_date = timezone.now() + timedelta(days=7)

            order.save()
            return Response({
                'status': 'Order ID generated',
                'ordercode': order.ordercode,
                'due_date': order.due_date
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Order code not provided'}, status=status.HTTP_400_BAD_REQUEST)

    
class UpdateCustomizedOrderView(APIView):
    def patch(self, request, order_id):
        try:
      
            order = CustomizedOrder.objects.get(id=order_id)
        except CustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

 
        serializer = CustomizedOrderSerializer(order, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteCustomizedOrderView(APIView):
    def delete(self, request, order_id):
        try:
        
            order = CustomizedOrder.objects.get(id=order_id)
            order.delete()  
            return Response({'message': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except CustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class FullCustomizedOrderListAPIView(APIView):
    def get(self, request):
     
        pending_orders = FullCustomizedOrder.objects.filter(status='pending')
        serializer = FullCustomizedOrderListSerializer(pending_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderFullApprovalView(APIView):
    def patch(self, request, pk):
        try:
            order = FullCustomizedOrder.objects.get(pk=pk)
        except FullCustomizedOrder.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        approved = request.data.get("approved")
        
        if approved is not None:
          
            order.status = 'approved' if approved else 'rejected'
            order.save()
            return Response({"message": "Order status updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)
        
class RejectFullOrderAPIView(APIView):
    def patch(self, request, pk):
        try:
            order = FullCustomizedOrder.objects.get(pk=pk)
        except FullCustomizedOrder.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
 
        order.status = 'rejected'
        order.save()

        serializer = FullCustomizedOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class  ApprovedFullOrdersView(APIView):
    def get(self, request):
        pending_orders = FullCustomizedOrder.objects.filter(status='approved')
        serializer = FullCustomizedOrderListSerializer(pending_orders, many=True)
        return Response(serializer.data)
    
 
    



class GenerateFullOrderIDView(APIView):
    def patch(self, request, pk=None):
        order = get_object_or_404(FullCustomizedOrder, pk=pk)
        ordercode = request.data.get('ordercode')
        due_date = request.data.get('due_date')   

        if ordercode:
            order.ordercode = ordercode

    
            if due_date:
                order.due_date = due_date
            else:
                 
                order.due_date = timezone.now() + timedelta(days=7)

            order.save()
            return Response({
                'status': 'Order ID generated',
                'ordercode': order.ordercode,
                'due_date': order.due_date
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Order code not provided'}, status=status.HTTP_400_BAD_REQUEST)





class UpdateFullCustomizedOrderView(APIView):
    def patch(self, request, order_id):
        try:
      
            order = FullCustomizedOrder.objects.get(id=order_id)
        except FullCustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

 
        serializer = FullCustomizedOrderSerializer(order, data=request.data, partial=True)
 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteFullCustomizedOrderView(APIView):
    def delete(self, request, order_id):
        try:
        
            order = FullCustomizedOrder.objects.get(id=order_id)
            order.delete()  
            return Response({'message': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except FullCustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class UpdateOrderStatusView(APIView):
    def patch(self, request, order_id):
        print("request",request.data)
        try:
            order = CustomizedOrder.objects.get(id=order_id)
        except CustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomizedOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("serializer.data",serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("serializer.data",serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateFullOrderStatusView(APIView):
    def patch(self, request, order_id):
        print("request",request.data)
        try:
            order = FullCustomizedOrder.objects.get(id=order_id)
        except FullCustomizedOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FullCustomizedOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("serializer.data",serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("serializer.data",serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 
 

 

class StatusCSVUploadView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        if not file.name.endswith('.csv'):
            return Response({'error': 'File type not supported. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        reader = csv.DictReader(decoded_file.splitlines())

        updated_orders = []
        not_found_orders = []  

        for row in reader:
            print(f"Row data: {row}") 

            order_id = row.get('Order Id')
            order_status = row.get('New Status').strip()  

            
            if not CustomizedOrder.objects.filter(ordercode=order_id).exists():
                print(f"Order with ordercode {order_id} does not exist.")
                not_found_orders.append(order_id)  
                continue   
            
   
            if order_status.lower() not in dict(CustomizedOrder.NEW_STATUS_CHOICES):
                print(f"Invalid status '{order_status}' for order {order_id}.")
                continue  
            try:
                order = CustomizedOrder.objects.get(ordercode=order_id)
                order.new_status = order_status.lower()   
                order.save()
                print(f"Order {order_id} status updated to {order_status}.")
                updated_orders.append(order_id)
            except Exception as e:
                print(f"Failed to update order {order_id}: {str(e)}")
                return Response({'error': f'Failed to update order {order_id}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
        response_data = {}
        if updated_orders:
            response_data['success'] = f'Updated statuses for orders: {updated_orders}'
        if not_found_orders:
            response_data['not_found'] = f'Orders not found: {not_found_orders}'

        return Response(response_data, status=status.HTTP_200_OK)


class StatusFullCSVUploadView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']

        if not file.name.endswith('.csv'):
            return Response({'error': 'File type not supported. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        reader = csv.DictReader(decoded_file.splitlines())

        updated_orders = []
        not_found_orders = []  

        for row in reader:
            print(f"Row data: {row}") 

            order_id = row.get('Order Id')
            order_status = row.get('New Status').strip()  

            
            if not FullCustomizedOrder.objects.filter(ordercode=order_id).exists():
                print(f"Order with ordercode {order_id} does not exist.")
                not_found_orders.append(order_id)  
                continue   
            
   
            if order_status.lower() not in dict(FullCustomizedOrder.NEW_STATUS_CHOICES):
                print(f"Invalid status '{order_status}' for order {order_id}.")
                continue  
            try:
                order = FullCustomizedOrder.objects.get(ordercode=order_id)
                order.new_status = order_status.lower()   
                order.save()
                print(f"Order {order_id} status updated to {order_status}.")
                updated_orders.append(order_id)
            except Exception as e:
                print(f"Failed to update order {order_id}: {str(e)}")
                return Response({'error': f'Failed to update order {order_id}: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
        response_data = {}
        if updated_orders:
            response_data['success'] = f'Updated statuses for orders: {updated_orders}'
        if not_found_orders:
            response_data['not_found'] = f'Orders not found: {not_found_orders}'

        return Response(response_data, status=status.HTTP_200_OK)
    

class ContactMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Optionally associate the message with the authenticated user
            serializer.validated_data['user'] = self.request.user

            try:
                # Save the contact message
                message = serializer.save()

                # Send email notification
                subject = f"New Contact Message from {message.full_name}"
                message_body = f"Name: {message.full_name}\nEmail: {message.email}\nPhone: {message.phone}\nMessage:\n{message.message}"
                recipient_email = settings.EMAIL_HOST_USER

                try:
                    send_mail(subject, message_body, settings.EMAIL_HOST_USER, [recipient_email])
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(f"Error sending email: {e}")
                    return Response({'status': 500, 'error': 'Failed to send email notification. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                print(f"Error saving contact message: {e}")
                return Response({'status': 500, 'error': 'Failed to save contact message. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 