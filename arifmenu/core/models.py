from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Place(models.Model):
    TYPES = [("restaurant", "Restaurant"), ("cafe", "Café"), ("hotel", "Hotel"),
             ("fastfood", "Fast food"), ("bar", "Bar & lounge"), ("bakery", "Bakery")]
    EMOJI = {"restaurant": "🍛", "cafe": "☕", "hotel": "🏨", "fastfood": "🍔", "bar": "🍹", "bakery": "🥐"}
    PLANS = [("free", "Free"), ("premium", "Premium")]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="places")
    name = models.CharField(max_length=150)
    place_type = models.CharField(max_length=20, choices=TYPES, default="restaurant", verbose_name="Type")
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    area = models.CharField(max_length=100, help_text="e.g. Bole, Piassa")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    opening_hours = models.CharField(max_length=120, blank=True, help_text="e.g. Mon-Sat 7:00-22:00")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    cover = models.ImageField(upload_to="covers/", blank=True)
    plan = models.CharField(max_length=20, choices=PLANS, default="free")
    is_active = models.BooleanField(default=False, help_text="Approved by admin")
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "place"
            slug, n = base, 2
            while Place.objects.filter(slug=slug).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def emoji(self):
        return self.EMOJI.get(self.place_type, "🍽")

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    place = models.ForeignKey(Place, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=80, help_text="e.g. Fasting, Breakfast, Drinks")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to="items/", blank=True)
    is_available = models.BooleanField(default=True, verbose_name="Available today")

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.place})"
