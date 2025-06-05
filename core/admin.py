from django.contrib import admin
from .models import Branch, PropertyEnquiry, ValuationRequest, Appointments

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'postal_code', 'phone', 'email']
    list_filter = ['city', 'state']
    search_fields = ['name', 'street_address', 'city', 'postal_code', 'phone', 'email']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone')
        }),
        ('Location', {
            'fields': (
                ('street_address', 'city'),
                ('state', 'postal_code'),
                ('latitude', 'longitude')
            )
        })
    )

@admin.register(PropertyEnquiry)
class PropertyEnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'property', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'message', 'property__street_address']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Details', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Enquiry Details', {
            'fields': ('property', 'message', 'created_at')
        })
    )

@admin.register(ValuationRequest)
class ValuationRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'property_address', 'property_type', 'created_at']
    list_filter = ['property_type', 'city', 'created_at']
    search_fields = ['name', 'email', 'street_address', 'city', 'postal_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Details', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Property Location', {
            'fields': (
                ('street_address', 'city'),
                ('state', 'postal_code')
            )
        }),
        ('Property Details', {
            'fields': ('property_type', 'bedrooms')
        }),
        ('Additional Information', {
            'fields': ('message', 'branch', ('created_at', 'updated_at'))
        })
    )

@admin.register(Appointments)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['get_property_address', 'first_name', 'last_name', 'preferred_date', 
                   'preferred_time', 'status', 'created_at']
    list_filter = ['status', 'preferred_date', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 
                    'property__street_address', 'property__city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Client Details', {
            'fields': (
                ('first_name', 'last_name'),
                ('email', 'phone'),
                'address'
            )
        }),
        ('Appointment Details', {
            'fields': (
                'property',
                ('preferred_date', 'preferred_time'),
                'status',
                'message'
            )
        }),
        ('System Fields', {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',)
        })
    )

    def get_property_address(self, obj):
        return obj.property.title
    get_property_address.short_description = 'Property'
    get_property_address.admin_order_field = 'property__street_address'
