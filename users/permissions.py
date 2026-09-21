from rest_framework import permissions


class IsLandlord(permissions.BasePermission):
    """
    Разрешение для арендодателей / Landlord permission.

    Чтение доступно всем, запись только арендодателям-владельцам объекта.
    Read access for all, write access only for landlords who own the object.
    """

    def has_permission(self, request, view) -> bool:
        """
        Проверяет принадлежность к группе Landlord для небезопасных методов.
        Checks Landlord group membership for unsafe methods.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.groups.filter(name='Landlord').exists()

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Проверяет что пользователь является владельцем объекта и арендодателем.
        Checks that user is object owner and a landlord.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user and request.user.groups.filter(name='Landlord').exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение для владельцев объектов / Owner or read-only permission.

    Чтение доступно всем авторизованным, запись только владельцу объекта.
    Read access for all authenticated users, write only for object owner.
    """

    def has_permission(self, request, view) -> bool:
        """
        Проверяет аутентификацию для небезопасных методов.
        Checks authentication for unsafe methods.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Проверяет что пользователь является владельцем объекта.
        Checks that user is the object owner.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsTenant(permissions.BasePermission):
    """
    Разрешение для арендаторов / Tenant permission.

    Чтение доступно всем, запись только арендаторам.
    Read access for all, write access only for tenants.
    """

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.groups.filter(name='Tenant').exists()
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.tenant == request.user and request.user.groups.filter(name='Tenant').exists()


class IsSelfOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsTenantOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.tenant == request.user