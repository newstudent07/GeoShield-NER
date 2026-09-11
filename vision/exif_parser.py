import io
from PIL import Image
import piexif

def _convert_to_degrees(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degrees in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def extract_exif_metadata(image_bytes: bytes) -> dict:
    """
    Extracts GPS and timestamp metadata from an image.
    Handles stripped or missing EXIF tags gracefully.
    """
    result = {
        "gps_status": "UNVERIFIED_GPS",
        "latitude": None,
        "longitude": None,
        "timestamp": None
    }
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        if "exif" not in img.info:
            return result
            
        exif_dict = piexif.load(img.info["exif"])
        
        # Extract Timestamp
        if piexif.ExifIFD.DateTimeOriginal in exif_dict.get("Exif", {}):
            dt_bytes = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
            result["timestamp"] = dt_bytes.decode('utf-8') if isinstance(dt_bytes, bytes) else str(dt_bytes)
            
        # Extract GPS
        gps_ifd = exif_dict.get("GPS", {})
        if gps_ifd:
            lat_ref = gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef)
            lat = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
            lon_ref = gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef)
            lon = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
            
            if lat and lon and lat_ref and lon_ref:
                lat_ref = lat_ref.decode('utf-8') if isinstance(lat_ref, bytes) else str(lat_ref)
                lon_ref = lon_ref.decode('utf-8') if isinstance(lon_ref, bytes) else str(lon_ref)
                
                lat_deg = _convert_to_degrees(lat)
                if lat_ref != "N":
                    lat_deg = -lat_deg
                    
                lon_deg = _convert_to_degrees(lon)
                if lon_ref != "E":
                    lon_deg = -lon_deg
                    
                result["latitude"] = lat_deg
                result["longitude"] = lon_deg
                result["gps_status"] = "VERIFIED"
                
    except Exception as e:
        # Gracefully handle all parsing errors, corrupted tags, etc.
        # It defaults to UNVERIFIED_GPS due to initialization above.
        pass
        
    return result
