from django.urls import path
from rest_framework.routers import DefaultRouter

from coupons.views.coupon import CouponViewSet
from coupons.views.coupon_code import CouponCodeViewSet

router = DefaultRouter()

urlpatterns = [
    path('', CouponViewSet.as_view({'get': 'list', 'post': 'create'}), name='coupon-list-create'),
    path('/<uuid:pk>', CouponViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='coupon-detail'),
    path('/<uuid:pk>/codes', CouponCodeViewSet.as_view({'get': 'list', 'post': 'create'}), name='coupon-codes-list-create'),
    path('/codes/<code>', CouponCodeViewSet.as_view({'patch': 'partial_update'}), name='coupon-code-detail'),
    path('/codes/<code>/check', CouponCodeViewSet.as_view({'get': 'check_availability'}), name='couponcode-check'),
    path('/codes/<code>/usage', CouponCodeViewSet.as_view({'get': 'check_usage'}), name='couponcode-usage'),
]
