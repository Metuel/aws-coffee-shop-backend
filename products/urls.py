from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ChoicesView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products',   ProductViewSet,   basename='product')

urlpatterns = [
    path('choices/', ChoicesView.as_view(), name='choices'),
] + router.urls