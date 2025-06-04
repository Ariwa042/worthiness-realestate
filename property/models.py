from django.db import models
from django.utils.text import slugify
from core.models import Branch

class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ]
    
    LISTING_TYPES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]
    
    # Address fields
    street_address = models.CharField(max_length=255, null=True, blank=True, help_text="Street number and name")
    city = models.CharField(max_length=100, null=True, blank=True, help_text="City/Town")
    state = models.CharField(max_length=100, null=True, blank=True, help_text="State/County/Region")
    postal_code = models.CharField(max_length=10, null=True, blank=True, help_text="Postal/ZIP Code")
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Asking price if for sale, monthly rent if for rent")
    
    floor_plan_image = models.ImageField(upload_to='properties/floor_plans/%Y/%m/%d/', blank=True, null=True)
    epc_image = models.ImageField(upload_to='properties/epc/%Y/%m/%d/', blank=True, null=True)
    
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPES)
    property_status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('under_offer', 'Under Offer'),    ], default='available')
    slug = models.SlugField(unique=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    @property
    def title(self):
        """Generate title from address components"""
        return f"{self.street_address}, {self.city}, {self.postal_code}"

    def save(self, *args, **kwargs):
        # Generate slug from address instead of title
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f'Image for {self.property.title}'

