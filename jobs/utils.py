import requests
import json
import math
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


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    Returns distance in miles.
    
    Args:
        lat1, lon1: First point coordinates (latitude, longitude)
        lat2, lon2: Second point coordinates (latitude, longitude)
    
    Returns:
        float: Distance in miles
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in miles
    r = 3959
    
    return c * r


def filter_jobs_by_distance(jobs, user_lat, user_lon, max_distance_miles):
    """
    Filter jobs by distance from user's location.

    Args:
        jobs: List of job dictionaries with latitude/longitude
        user_lat: User's latitude
        user_lon: User's longitude
        max_distance_miles: Maximum distance in miles

    Returns:
        list: Filtered and sorted jobs by distance
    """
    filtered_jobs = []
    for job in jobs:
        distance = calculate_distance(
            user_lat, user_lon,
            float(job['latitude']), float(job['longitude'])
        )
        if distance <= max_distance_miles:
            job['distance'] = round(distance, 1)
            filtered_jobs.append(job)

    # Sort by distance
    filtered_jobs.sort(key=lambda x: x['distance'])
    return filtered_jobs


def calculate_skill_match_score(profile_skills, job_skills):
    """
    Calculate a match score between a profile's skills and a job's required skills.
    Uses case-insensitive matching and partial word matching.

    Args:
        profile_skills: List or comma-separated string of profile skills
        job_skills: List or comma-separated string of job required skills

    Returns:
        dict: {
            'score': float (0-100),
            'matched_skills': list of matching skills,
            'total_job_skills': int
        }
    """
    # Normalize inputs to lowercase lists
    if isinstance(profile_skills, str):
        profile_skills = [skill.strip().lower() for skill in profile_skills.split(',') if skill.strip()]
    else:
        profile_skills = [skill.strip().lower() for skill in profile_skills if skill.strip()]

    if isinstance(job_skills, str):
        job_skills = [skill.strip().lower() for skill in job_skills.split(',') if skill.strip()]
    else:
        job_skills = [skill.strip().lower() for skill in job_skills if skill.strip()]

    if not job_skills or not profile_skills:
        return {
            'score': 0.0,
            'matched_skills': [],
            'total_job_skills': len(job_skills)
        }

    # Find matching skills (exact and partial matches)
    matched_skills = []
    for job_skill in job_skills:
        for profile_skill in profile_skills:
            # Exact match or partial word match
            if (job_skill == profile_skill or
                job_skill in profile_skill or
                profile_skill in job_skill):
                matched_skills.append(job_skill)
                break

    # Calculate score as percentage of required skills matched
    score = (len(matched_skills) / len(job_skills)) * 100

    return {
        'score': round(score, 1),
        'matched_skills': matched_skills,
        'total_job_skills': len(job_skills)
    }


def get_job_recommendations(user_profile, limit=20):
    """
    Get personalized job recommendations for a job seeker based on their skills.

    Args:
        user_profile: Profile model instance for the job seeker
        limit: Maximum number of recommendations to return

    Returns:
        list: List of job dictionaries with match scores, sorted by relevance
    """
    from jobs.models import Job

    # Get active jobs
    jobs = Job.objects.filter(status='active')

    # Get user's skills
    user_skills = user_profile.get_skills_list()

    if not user_skills:
        # If user has no skills, return recent jobs
        return []

    recommendations = []

    for job in jobs:
        job_skills = job.get_skills_list()

        # Calculate skill match score
        match_result = calculate_skill_match_score(user_skills, job_skills)

        # Only include jobs with at least some skill match
        if match_result['score'] > 0:
            recommendations.append({
                'job': job,
                'match_score': match_result['score'],
                'matched_skills': match_result['matched_skills'],
                'matched_count': len(match_result['matched_skills']),
                'total_job_skills': match_result['total_job_skills'],
            })

    # Sort by match score (highest first), then by creation date (newest first)
    recommendations.sort(key=lambda x: (x['match_score'], x['job'].created_at), reverse=True)

    # Apply limit
    return recommendations[:limit]
