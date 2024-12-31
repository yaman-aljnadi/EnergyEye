from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
    # Import and connect signals here
        import website.signals  # Replace 'myapp' with the name of your app
