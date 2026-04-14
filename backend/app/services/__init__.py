# AgriVerse Services Package
# Import all services to make them available

try:
    from . import gemini_client
except ImportError as e:
    print(f"Warning: Could not import gemini_client: {e}")

try:
    from . import disease_detector
except ImportError as e:
    print(f"Warning: Could not import disease_detector: {e}")

try:
    from . import voice_service
except ImportError as e:
    print(f"Warning: Could not import voice_service: {e}")

try:
    from . import advisory_service
except ImportError as e:
    print(f"Warning: Could not import advisory_service: {e}")

try:
    from . import translation_service
except ImportError as e:
    print(f"Warning: Could not import translation_service: {e}")

__all__ = ['gemini_client', 'disease_detector', 'voice_service', 'advisory_service', 'translation_service']