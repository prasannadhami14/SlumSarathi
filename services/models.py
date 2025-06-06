from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import User
import uuid

class ServiceCategory(models.Model):
    """Categories for organizing services"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_('name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('slug'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_('icon'),
                          help_text=_("Icon class from your icon library"))
    
    class Meta:
        verbose_name = _('service category')
        verbose_name_plural = _('service categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Service(models.Model):
    """Model for student services being offered"""
    SERVICE_TYPES = (
        ('teaching', _('Teaching/Tutoring')),
        ('assignment', _('Assignment Help')),
        ('consulting', _('Academic Consulting')),
        ('other', _('Other Service')),
    )
    
    PRICING_MODELS = (
        ('hourly', _('Hourly Rate')),
        ('fixed', _('Fixed Price')),
        ('free', _('Free Service')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='services_offered',
        limit_choices_to={'user_type': 1},  # Only students can provide services
        verbose_name=_('provider')
    )
    title = models.CharField(max_length=200, verbose_name=_('title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('slug'))
    description = models.TextField(verbose_name=_('description'))
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name=_('service type'))
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name=_('category')
    )
    
    # Pricing information
    pricing_model = models.CharField(max_length=20, choices=PRICING_MODELS, verbose_name=_('pricing model'))
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('rate')
    )
    is_free = models.BooleanField(default=False, verbose_name=_('is free'))
    
    # Availability
    is_available = models.BooleanField(default=True, verbose_name=_('is available'))
    available_from = models.DateField(null=True, blank=True, verbose_name=_('available from'))
    available_to = models.DateField(null=True, blank=True, verbose_name=_('available to'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))
    views = models.PositiveIntegerField(default=0, verbose_name=_('views'))
    
    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['service_type']),
            models.Index(fields=['pricing_model']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.provider.email}"
    
    def save(self, *args, **kwargs):
        """Ensure pricing consistency"""
        if self.pricing_model == 'free':
            self.is_free = True
            self.rate = None
        elif self.rate is None or self.rate <= 0:
            self.pricing_model = 'free'
            self.is_free = True
            self.rate = None
        else:
            self.is_free = False
        super().save(*args, **kwargs)
    
    @property
    def display_price(self):
        if self.is_free:
            return _("Free")
        if self.pricing_model == 'hourly':
            return _("${rate}/hour").format(rate=self.rate)
        return _("${rate} (fixed)").format(rate=self.rate)

class ServiceImage(models.Model):
    """Images for services"""
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('service')
    )
    image = models.ImageField(upload_to='service_images/', verbose_name=_('image'))
    caption = models.CharField(max_length=100, blank=True, verbose_name=_('caption'))
    is_featured = models.BooleanField(default=False, verbose_name=_('is featured'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('order'))
    
    class Meta:
        verbose_name = _('service image')
        verbose_name_plural = _('service images')
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.service.title}"

class ServiceRequest(models.Model):
    """Model for service requests from other users"""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name=_('service')
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_requests',
        verbose_name=_('requester')
    )
    message = models.TextField(verbose_name=_('message'))
    proposed_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('proposed rate')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('status')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))
    
    class Meta:
        verbose_name = _('service request')
        verbose_name_plural = _('service requests')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'requester'],
                condition=models.Q(status='pending'),
                name='unique_pending_request'
            )
        ]
    
    def __str__(self):
        return f"Request for {self.service.title} by {self.requester.email}"
    
    def accept(self):
        """Accept the service request"""
        if self.status != 'pending':
            raise ValueError(_("Only pending requests can be accepted"))
        self.status = 'accepted'
        self.save()
    
    def reject(self):
        """Reject the service request"""
        if self.status != 'pending':
            raise ValueError(_("Only pending requests can be rejected"))
        self.status = 'rejected'
        self.save()

class ServiceReview(models.Model):
    """Reviews for services"""
    RATING_CHOICES = (
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('service')
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_reviews',
        verbose_name=_('reviewer')
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name=_('rating'))
    comment = models.TextField(blank=True, verbose_name=_('comment'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('updated at'))
    
    class Meta:
        verbose_name = _('service review')
        verbose_name_plural = _('service reviews')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'reviewer'],
                name='one_review_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.get_rating_display()} review for {self.service.title}"
    
    @property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)