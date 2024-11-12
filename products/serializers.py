from rest_framework import serializers
from .models import *


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'usertype']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'image'] 
        
        
class ProductMultipleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMultipleImages
        fields = ['id', 'image']

 

class ProductSerializer(serializers.ModelSerializer):
    usertypes = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all(), many=True)
    additional_images = ProductMultipleImagesSerializer(many=True, required=False) 
      

    class Meta:
        model = Product  
        fields = ['id', 'SKU', 'product_name', 'category',   'color', 
                  'gross_weight', 'diamond_weight', 'colour_stones', 
                  'net_weight', 'product_size', 'description', 
                  'usertypes', 'product_image', 'additional_images'] 


class ProductListSerializer(serializers.ModelSerializer):
    usertypes = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all(), many=True)
    additional_images = ProductMultipleImagesSerializer(many=True, required=False)
    category_name = serializers.SerializerMethodField()

    product_image = serializers.SerializerMethodField()   

    class Meta:
        model = Product
        fields = [
            'id', 'SKU', 'product_name', 'category', 'category_name',
            'color', 'gross_weight', 'diamond_weight', 'colour_stones',
            'net_weight', 'product_size', 'description',
            'usertypes', 'product_image', 'additional_images'
        ]

    def get_category_name(self, obj):
        return obj.category.category_name if obj.category else None

    def get_product_image(self, obj):
        if obj.product_image:
            return obj.product_image.url  # Return the URL if the image exists
        return None  

    
    
    
    
class CustomizedProductMultipleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomizedProductMultipleImages
        fields = ['id', 'image']


 

class CustomizedProductSerializer(serializers.ModelSerializer):
    usertypes = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all(), many=True)
    additional_images = CustomizedProductMultipleImagesSerializer(many=True, required=False)   

    class Meta:
        model = CustomizedProduct  
        fields = ['id', 'SKU', 'product_name', 'category',   'color', 
                  'gross_weight', 'diamond_weight', 'colour_stones', 
                  'net_weight', 'product_size', 'description', 
                  'usertypes', 'product_image', 'additional_images'] 


class CustomizedProductListSerializer(serializers.ModelSerializer):
    usertypes = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all(), many=True)
    additional_images = CustomizedProductMultipleImagesSerializer(many=True, required=False)  
    category_name = serializers.SerializerMethodField()   

    class Meta:
        model = CustomizedProduct
        fields = ['id', 'SKU', 'product_name','category', 'category_name', 
                  'color', 'gross_weight', 'diamond_weight', 'colour_stones', 
                  'net_weight', 'product_size', 'description', 
                  'usertypes', 'product_image', 'additional_images']

    def get_category_name(self, obj):
        return obj.category.category_name if obj.category else None 
    
    
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    usertypes = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all())  # Add this line

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email',
            'mobile_number',
            'whatsapp_number',
            'company_name',
            'billing_address',
            'shipping_address',
            'company_logo',
            'company_email',
            'company_website',
            'username',
            'password',
            'confirm_password',
            'usertypes',  
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        confirm_password = validated_data.pop('confirm_password', None)

    
        if validated_data['password'] != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

 

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Ensure password is write-only
    usertypes = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all(), allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email',
            'mobile_number',
            'whatsapp_number',
            'company_name',
            'billing_address',
            'shipping_address',
            'company_logo',
            'company_email',
            'company_website',
            'username',
            'password',
            'usertypes',
        ]

    def validate_email(self, value):
        if self.instance and value != self.instance.email:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate_username(self, value):
        if self.instance and value != self.instance.username:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("User with this username already exists.")
        return value

    def update(self, instance, validated_data):
    
        password = validated_data.pop('password', None)   

    
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

       
        if password:
            instance.password = make_password(password)

        instance.save()   
        return instance
    
    

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'image']
        
from rest_framework import serializers
from .models import Cart, Product  

class CartSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)   

    class Meta:
        model = Cart
        fields = ['id','product_id', 'quantity']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        quantity = validated_data.get('quantity', 1)  

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")

       
        print(f"Creating cart item: Product ID: {product.id}, Colour Stones: {product.colour_stones}, Quantity: {quantity}")
 
        gross_weight = product.gross_weight * quantity
        diamond_weight = (product.diamond_weight or 0) * quantity
        colour_stones = product.colour_stones * quantity  
        net_weight = product.net_weight * quantity

     
        cart = Cart(
            user=validated_data.get('user'),
            product=product,
            quantity=quantity,
            gross_weight=gross_weight,
            diamond_weight=diamond_weight,
            colour_stones=colour_stones,  
            net_weight=net_weight,
        )
        cart.save()
        print("New item added:", {
            'id': cart.id,
            'product_id': cart.product.id,
            'quantity': cart.quantity,
            'colour_stones': cart.colour_stones,
            'gross_weight': cart.gross_weight,
            'diamond_weight': cart.diamond_weight,
            'net_weight': cart.net_weight,
        })

        return cart
 


 
# class CartGetSerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField(write_only=True) 
#     product = ProductSerializer(read_only=True)  

#     class Meta:
#         model = Cart
#         fields = ['id','product_id', 'quantity', 'product','gross_weight','colour_stones','diamond_weight','net_weight']  


class CartTotalSerializer(serializers.Serializer):
    total_gross_weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_diamond_weight = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_colour_stones = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_net_weight = serializers.DecimalField(max_digits=10, decimal_places=2)

class CartGetSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True) 
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product_id', 'quantity', 'product', 'gross_weight', 'colour_stones', 'diamond_weight', 'net_weight']

# class OrderItemSerializer(serializers.ModelSerializer):
#     product = serializers.CharField(source='product.code')  

#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'quantity', 'additional_notes']

#     def create(self, validated_data):
      
#         product_data = validated_data.pop('product')  
#         product_code = product_data['code'] 
        
#         try:
          
#             product = Product.objects.get(code=product_code)
#         except Product.DoesNotExist:
#             raise serializers.ValidationError({"product": "Product does not exist."})
        
       
#         order_item = OrderItem.objects.create(product=product, **validated_data)
#         return order_item




class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField()  

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'additional_notes']

    def create(self, validated_data):
        sku = validated_data.pop('product')  
        try:
            product = Product.objects.get(SKU=sku)  
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "Product does not exist."})
        
    
        return OrderItem.objects.create(product=product, **validated_data)


from decimal import Decimal, InvalidOperation

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_gross_weight', 'total_diamond_weight', 
                  'total_colour_stones', 'total_net_weight', 'created_at', 'order_items']
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        total_gross_weight = Decimal(0.00)
        total_diamond_weight = Decimal(0.00)
        total_colour_stones = Decimal(0.00)
        total_net_weight = Decimal(0.00)

        for item_data in order_items_data:
            sku = item_data.pop('product')   
            try:
                product = Product.objects.get(SKU=sku) 
            except Product.DoesNotExist:
                raise serializers.ValidationError({"product": "Product does not exist."})

           
            try:
                colour_stones_value = Decimal(product.colour_stones) if product.colour_stones else Decimal(0.00)
            except InvalidOperation:
                raise serializers.ValidationError({"colour_stones": "Invalid colour stones value."})

           
            total_gross_weight += product.gross_weight * Decimal(item_data['quantity'])
            total_diamond_weight += product.diamond_weight * Decimal(item_data['quantity'])
            total_colour_stones += colour_stones_value * Decimal(item_data['quantity'])
            total_net_weight += product.net_weight * Decimal(item_data['quantity'])

         
            OrderItem.objects.create(order=order, product=product, **item_data)

        
        order.total_gross_weight = total_gross_weight
        order.total_diamond_weight = total_diamond_weight
        order.total_colour_stones = total_colour_stones
        order.total_net_weight = total_net_weight
        order.save()  

        return order
class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'mobile_number',
            'whatsapp_number',
            'company_name',
            'billing_address',
            'shipping_address',
            'company_logo',
            'company_email',
            'company_website',
            'username',
            'usertypes',
            'prof_image',  
        ]

    def update(self, instance, validated_data):
        if 'prof_image' in validated_data:
            instance.prof_image = validated_data['prof_image']  
        return super().update(instance, validated_data)


class OrderItemSerializerss(serializers.ModelSerializer):
    product = ProductListSerializer()   

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity',  'additional_notes']
        
        
class OrderSerializerss(serializers.ModelSerializer):
    order_items = OrderItemSerializerss(many=True)
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ['id', 'ordercode', 'user', 'total_gross_weight', 'total_diamond_weight', 
                  'total_colour_stones', 'total_net_weight', 'created_at', 'order_items']
        extra_kwargs = {'user': {'read_only': True}}
        
 
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color']
        
from rest_framework import serializers

class CustomizedOrderSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)  
    color = ColorSerializer(read_only=True)       
    user = UserSerializer(read_only=True)       

    class Meta:
        model = CustomizedOrder
        fields = [
            'id', 'new_status', 'product', 'size', 'user','gram', 'ordercode', 
            'cent', 'color', 'description', 'quantity', 'due_date'
        ]
        extra_kwargs = {'user': {'read_only': True}}

    def validate_new_status(self, value):
        valid_choices = [choice[0] for choice in CustomizedOrder.NEW_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid new_status. Choose from {valid_choices}.")
        return value




 

class CustomizedOrderCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=CustomizedProduct.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all())
    user = serializers.ReadOnlyField(source='user.id')   

    class Meta:
        model = CustomizedOrder
        fields = ['id', 'new_status', 'product', 'size', 'user', 'gram', 'ordercode', 'cent', 'color', 'description', 'quantity', 'due_date']
        extra_kwargs = {'user': {'read_only': True}}

    def validate_new_status(self, value):
        valid_choices = [choice[0] for choice in CustomizedOrder.NEW_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid new_status. Choose from {valid_choices}.")
        return value
       
        
class ColorupdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color']

    def update(self, instance, validated_data):
        instance.color = validated_data.get('color', instance.color)
        instance.save()  
        return instance
    
class FullCustomizedMultipleImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FullCustomizedMultipleImages
        fields = ['id','image']   


class FullCustomizedOrderListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  
    color = ColorSerializer(read_only=True)       
    user = UserSerializer(read_only=True)  
    additional_images = FullCustomizedMultipleImagesSerializer(many=True, read_only=True, source='full_additional_images')

    class Meta:
        model = FullCustomizedOrder
        fields = [
            'id','user','new_status' ,'category' ,'due_date', 'design_number',
            'size', 'gram', 'cent', 'color', 
            'description', 'quantity', 'ordercode', 
            'status', 'additional_images'
        ]
    def validate_new_status(self, value):
    
        valid_choices = [choice[0] for choice in CustomizedOrder.NEW_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid new_status. Choose from {valid_choices}.")
        return value

class FullCustomizedOrderSerializer(serializers.ModelSerializer):
    category= serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all())
    user = serializers.ReadOnlyField(source='user.id')
    additional_images = FullCustomizedMultipleImagesSerializer(many=True, read_only=True, source='full_additional_images')

    class Meta:
        model = FullCustomizedOrder
        fields = [
            'id','user','new_status' ,'category','due_date', 'design_number',
            'size', 'gram', 'cent', 'color', 
            'description', 'quantity', 'ordercode', 
            'status', 'additional_images'
        ]
    def validate_new_status(self, value):
    
        valid_choices = [choice[0] for choice in CustomizedOrder.NEW_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid new_status. Choose from {valid_choices}.")
        return value
class OrderIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'ordercode']
        
        
 
 

class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'quantity']  


 

class OrderUpdateSerializer(serializers.ModelSerializer):
    order_items = OrderItemUpdateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'ordercode', 'order_items']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'message', 'created_at']