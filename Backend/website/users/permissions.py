from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    """
    Allows access only to customers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer

class IsSeller(BasePermission):
    """
    Allows access only to sellers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_seller
