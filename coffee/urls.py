from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Authentication ---
    path('api/auth/', include('accounts.urls')),
    path('api/auth/login/', auth_views.obtain_auth_token, name='api_token'),

    # --- App endpoints ---
    path('api/', include('products.urls')),
    path('api/cart/', include('carts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/bookings/', include('bookings.urls')),

]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)









# """
# URL configuration for coffee project.
# """
# from django.contrib import admin
# from django.urls import path, include
# from django.conf.urls.static import static
# from django.conf import settings
# from rest_framework.authtoken import views as auth_views
# from dj_rest_auth.views import LoginView, LogoutView
# from dj_rest_auth.registration.views import RegisterView


# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # --- Auth ---
#     # Override login/register/logout so an expired token in the header
#     # doesn't block these endpoints.
#     path('api/auth/login/',
#          LoginView.as_view(authentication_classes=[]),
#          name='rest_login'),
#     path('api/auth/logout/',
#          LogoutView.as_view(authentication_classes=[]),
#          name='rest_logout'),
#     path('api/auth/registration/',
#          RegisterView.as_view(authentication_classes=[]),
#          name='rest_register'),

#     # Everything else from dj-rest-auth (password reset, user, token refresh, etc.)
#     path('api/auth/', include('dj_rest_auth.urls')),

#     # --- App endpoints ---
#     path('api/',        include('products.urls')),
#     path('api/cart/',   include('carts.urls')),
#     path('api/token/', auth_views.obtain_auth_token, name='api_token'),
#     # path('api/orders/', include('orders.urls')),

# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)