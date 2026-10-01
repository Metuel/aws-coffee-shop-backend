from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .choices import PRODUCT_TYPES, SIZES


class ChoicesView(APIView):
    """GET /api/choices/ — values the frontend needs for dropdowns & filters."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({
            'product_types': PRODUCT_TYPES,
            'sizes':         SIZES,
            'dietary_flags': [
                {'key': 'is_vegetarian',  'label': 'Vegetarian'},
                {'key': 'is_vegan',       'label': 'Vegan'},
                {'key': 'is_gluten_free', 'label': 'Gluten-Free'},
                {'key': 'contains_nuts',  'label': 'Contains Nuts'},
            ],
        })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()

        if not self.request.user.is_staff:
            qs = qs.filter(is_available=True)

        params = self.request.query_params

        if params.get('product_type'):
            qs = qs.filter(product_type=params['product_type'])
        if params.get('size'):
            qs = qs.filter(size=params['size'])
        if params.get('category'):
            qs = qs.filter(category_id=params['category'])

        for flag in ('is_vegetarian', 'is_vegan', 'is_gluten_free',
                     'contains_nuts', 'is_featured'):
            val = params.get(flag)
            if val is not None:
                if val.lower() in ('true', '1', 'yes'):
                    qs = qs.filter(**{flag: True})
                elif val.lower() in ('false', '0', 'no'):
                    qs = qs.filter(**{flag: False})

        if params.get('price_min'):
            qs = qs.filter(price__gte=params['price_min'])
        if params.get('price_max'):
            qs = qs.filter(price__lte=params['price_max'])

        return qs