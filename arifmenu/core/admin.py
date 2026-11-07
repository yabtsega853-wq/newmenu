from django.contrib import admin
from .models import MenuItem, Place


class ItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "place_type", "area", "owner", "plan", "is_active", "is_featured", "views")
    list_filter = ("place_type", "is_active", "is_featured", "plan", "area")
    list_editable = ("is_active", "is_featured", "plan")
    search_fields = ("name", "area", "owner__username")
    inlines = [ItemInline]


admin.site.register(MenuItem)
