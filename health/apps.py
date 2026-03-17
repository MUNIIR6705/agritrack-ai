from django.apps import AppConfig

class HealthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'health'
    verbose_name = 'AgriTrack Health & Identity'

    def ready(self):
        """
        Activates the Identity Node signals.
        This automatically creates a UserProfile whenever a User is created.
        """
        try:
            import health.signals  # noqa
        except ImportError:
            pass