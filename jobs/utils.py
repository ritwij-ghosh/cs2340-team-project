import requests
import json
from django.conf import settings
from django.db.models import Q


def geocode_location(location_string):
    """
    Convert a location string to latitude and longitude coordinates.
    Uses OpenStreetMap Nominatim API (free, no API key required).
    
    Args:
        location_string (str): Location string like "Atlanta, GA" or "New York, NY"
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails
    """
    if not location_string or location_string.lower() in ['remote', 'anywhere']:
        return None, None
    
    try:
        # Use OpenStreetMap Nominatim API (free)
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': location_string,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'HireBuzz/1.0 (Job Board Application)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            return lat, lon
            
    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        print(f"Geocoding error for '{location_string}': {e}")
    
    return None, None


def geocode_job_locations():
    """
    Geocode all jobs that don't have coordinates yet.
    This is a utility function to populate existing jobs with coordinates.
    """
    from jobs.models import Job
    
    jobs_without_coords = Job.objects.filter(
        latitude__isnull=True,
        longitude__isnull=True
    ).exclude(
        Q(location__isnull=True) | Q(location='') | Q(location__in=['Remote', 'remote', 'Anywhere', 'anywhere'])
    )
    
    geocoded_count = 0
    
    for job in jobs_without_coords:
        lat, lon = geocode_location(job.location)
        if lat is not None and lon is not None:
            job.latitude = lat
            job.longitude = lon
            job.save()
            geocoded_count += 1
            print(f"Geocoded: {job.title} at {job.location} -> ({lat}, {lon})")
        else:
            print(f"Failed to geocode: {job.title} at {job.location}")
    
    print(f"Successfully geocoded {geocoded_count} jobs")
    return geocoded_count
