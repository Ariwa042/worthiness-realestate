from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Property, PropertyImage
from core.models import Appointments
from core.forms import AppointmentForm
from urllib.parse import quote
import requests
import json

def get_coordinates(address):
    """Get coordinates from OpenStreetMap Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={quote(address)}"
        headers = {'User-Agent': 'RealEstate/1.0'}  # Nominatim requires a User-Agent
        response = requests.get(url, headers=headers)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        return None
    except Exception:
        return None

def property_list(request):
    properties = Property.objects.filter(property_status='available')
    context = {
        'properties': properties,
    }
    return render(request, 'property/property_list.html', context)

def property_detail(request, slug):
    property = get_object_or_404(Property, slug=slug)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.property = property
                appointment.status = 'scheduled'
                appointment.save()
                
                messages.success(request, 'Your viewing request has been submitted successfully. We will contact you to confirm the appointment.')
                return redirect('property:property_detail', slug=slug)
            except Exception as e:
                messages.error(request, 'An error occurred while submitting your request. Please try again.')
                return redirect('property:property_detail', slug=slug)
    else:
        form = AppointmentForm()    # Get coordinates and create map URL for the property
    address = f"{property.street_address}, {property.city}, {property.postal_code}"
    coordinates = get_coordinates(address)
    
    map_url = None
    if coordinates:
        lat, lon = coordinates
        map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01}%2C{lat-0.01}%2C{lon+0.01}%2C{lat+0.01}&amp;layer=mapnik&amp;marker={lat}%2C{lon}"
    
    context = {
        'property': property,
        'coordinates': coordinates,
        'map_url': map_url,
        'form': form,
    }
    return render(request, 'property/property_detail.html', context)

def property_search(request):
    properties = Property.objects.filter(property_status='available')
    
    # Get filter parameters from request
    property_type = request.GET.get('type')
    listing_type = request.GET.get('listing')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    bedrooms = request.GET.get('bedrooms')
    city = request.GET.get('city')
    
    # Apply filters
    if property_type:
        properties = properties.filter(property_type=property_type)
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if bedrooms:
        properties = properties.filter(bedrooms=bedrooms)
    if city:
        properties = properties.filter(city__icontains=city)    # Create map URL with markers for all filtered properties
    valid_properties = []
    lat_sum = lon_sum = 0
    count = 0
    
    for prop in properties:
        if prop.street_address and prop.city:
            address = f"{prop.street_address}, {prop.city}, {prop.postal_code}"
            coordinates = get_coordinates(address)
            if coordinates:
                lat, lon = coordinates
                valid_properties.append((lat, lon, prop.title))
                lat_sum += lat
                lon_sum += lon
                count += 1
    
    map_url = None
    if count > 0:
        # Calculate center point of all properties
        center_lat = lat_sum / count
        center_lon = lon_sum / count        # Create the base map URL centered on all properties
        # Make the bounding box bigger to ensure all properties are visible
        map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={center_lon-0.1}%2C{center_lat-0.1}%2C{center_lon+0.1}%2C{center_lat+0.1}&amp;layer=mapnik"
        
        # Add markers for all properties - add them as separate marker parameters
        for lat, lon, title in valid_properties:
            map_url += f"&amp;marker={lat}%2C{lon}"
    context = {
        'properties': properties,
        'property_types': Property.PROPERTY_TYPES,
        'listing_types': Property.LISTING_TYPES,
        'map_url': map_url,
    }

    return render(request, 'property/property_search.html', context)
