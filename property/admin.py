from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'is_primary']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['street_address', 'city', 'property_type', 'listing_type', 
                   'price', 'bedrooms', 'property_status', 'featured']
    list_filter = ['property_type', 'listing_type', 'property_status', 
                  'city', 'featured', 'bedrooms']
    search_fields = ['street_address', 'city', 'postal_code', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    list_editable = ['featured', 'property_status']
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Location', {
            'fields': (
                ('street_address', 'city'),
                ('state', 'postal_code'),
            ),
            'classes': ('wide',)
        }),
        ('Property Details', {
            'fields': (
                'description',
                ('property_type', 'listing_type'),
                ('bedrooms', 'bathrooms'),
                'price',
                'property_status',
            )
        }),
        ('Media', {
            'fields': (
                'floor_plan_image',
                'epc_image',
            ),
            'classes': ('collapse',)
        }),
        ('Management', {
            'fields': (
                'featured',
                'slug',
                ('created_at', 'updated_at'),
            )
        })
    )
