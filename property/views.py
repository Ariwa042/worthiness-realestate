from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Property, PropertyImage
from core.models import Appointments
from core.forms import AppointmentForm
from urllib.parse import quote
import requests
import json
import folium
from statistics import mean

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
    
    # Get coordinates and create Folium map for the property
    address = f"{property.street_address}, {property.city}, {property.postal_code}"
    coordinates = get_coordinates(address)
    
    map_html = None
    if coordinates:
        lat, lon = coordinates
        # Create the map centered on the property
        m = folium.Map(location=[lat, lon], zoom_start=15)
        
        # Add a marker for the property
        popup_html = f"""
            <div style='width: 200px'>
                <h6>{property.title}</h6>
                <p>£{property.price:,.2f}<br>
                {property.bedrooms} bedrooms</p>
            </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)
        
        # Save map to HTML string
        map_html = m._repr_html_()
    
    context = {
        'property': property,
        'map_html': map_html,
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
        properties = properties.filter(price__gte=min_price).order_by('price')  # Order by price ascending
    if max_price:
        properties = properties.filter(price__lte=max_price).order_by('-price')  # Order by price descending
    if bedrooms:
        properties = properties.filter(bedrooms=bedrooms)
    if city:
        properties = properties.filter(city__icontains=city)
    
    # If max_price wasn't set but we have other filters, still order by price
    if not max_price and (property_type or listing_type or min_price or bedrooms or city):
        properties = properties.order_by('-price')
    
    # Create interactive map with Folium
    coordinates_list = []
    for prop in properties:
        if prop.street_address and prop.city:
            address = f"{prop.street_address}, {prop.city}, {prop.postal_code}"
            coordinates = get_coordinates(address)
            if coordinates:
                lat, lon = coordinates
                coordinates_list.append({
                    'lat': lat,
                    'lon': lon,
                    'title': prop.title,
                    'price': prop.price,
                    'bedrooms': prop.bedrooms,
                    'slug': prop.slug
                })
    map_html = None
    if coordinates_list:
        # Create the map with a default center
        m = folium.Map()
        
        # Create a feature group for all markers
        marker_group = folium.FeatureGroup()
        
        # Add markers for each property
        for prop in coordinates_list:
            popup_html = f"""
                <div style='width: 200px'>
                    <h6><a href='{reverse("property:property_detail", args=[prop["slug"]])}' target='_blank'>
                        {prop["title"]}
                    </a></h6>
                    <p>£{prop["price"]:,.2f}<br>
                    {prop["bedrooms"]} bedrooms</p>
                </div>
            """
            folium.Marker(
                location=[prop['lat'], prop['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='red', icon='home', prefix='fa')
            ).add_to(marker_group)
        
        # Add the marker group to the map
        marker_group.add_to(m)
        
        # Fit the map to the bounds of all markers
        try:
            sw = [min(item['lat'] for item in coordinates_list), min(item['lon'] for item in coordinates_list)]
            ne = [max(item['lat'] for item in coordinates_list), max(item['lon'] for item in coordinates_list)]
            m.fit_bounds([sw, ne], padding=(30, 30))  # Add padding around the bounds
        except ValueError:
            # If there's only one marker, center on it with a reasonable zoom
            m.location = [coordinates_list[0]['lat'], coordinates_list[0]['lon']]
            m.zoom_start = 15        # Save map to a temporary div
        map_html = m._repr_html_()
    
    context = {
        'properties': properties,
        'property_types': Property.PROPERTY_TYPES,
        'listing_types': Property.LISTING_TYPES,
        'map_html': map_html,
    }

    return render(request, 'property/property_search.html', context)
