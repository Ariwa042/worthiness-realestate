from django.db import models
from django.utils.text import slugify

# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255, help_text="Street number and name", blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, help_text="State/County/Region", blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def address(self):
        """Generate full address from components"""
        return f"{self.street_address}, {self.city}, {self.postal_code}"

    class Meta:
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name

class PropertyEnquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    property = models.ForeignKey('property.Property', on_delete=models.CASCADE, related_name='enquiries')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Property Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f'Enquiry from {self.name} for {self.property.title}'

class Appointments(models.Model):
    property = models.ForeignKey('property.Property', on_delete=models.CASCADE, related_name='viewings')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, null=True, blank=True) # Optional, address of the person requesting the appointment
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = 'Appointments'
        ordering = ['-created_at']
    def __str__(self):
        return f'Appointment for {self.property.title} by {self.first_name} {self.last_name}'

class ValuationRequest(models.Model):
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255, null=True, blank=True, help_text="Street number and name")
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, help_text="State/County/Region", null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    message = models.TextField(blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='valuation_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def property_address(self):
        """Generate full address from components"""
        return f"{self.street_address}, {self.city}, {self.postal_code}"

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Valuation request from {self.name} for {self.property_address}'

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    featured_image = models.ImageField(upload_to='pages/', blank=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
