from django.apps import AppConfig


class StandardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.standards"
    verbose_name = "Standards & Policy Configuration"

    def ready(self):
        import apps.standards.signals  # noqa: F401
