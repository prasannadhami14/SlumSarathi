from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import uuid
import os

def validate_pdf_file(value):
    """Custom validator to ensure only PDF files are uploaded"""
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('Only PDF files are allowed.')

def resource_file_path(instance, filename):
    """Generate file path for resources (PDF only)"""
    # Force .pdf extension
    filename = f"{uuid.uuid4()}.pdf"
    return os.path.join('resources/', filename)

class ResourceCategory(models.Model):
    """Categories for organizing resources"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('resource category')
        verbose_name_plural = _('resource categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Resource(models.Model):
    """Main model for notes, assignments, and books"""
    RESOURCE_TYPES = (
        ('note', 'Lecture Note'),
        ('assignment', 'Assignment'),
        ('book', 'Book/Textbook'),
        ('exam', 'Exam Paper'),
        ('other', 'Other'),
    )
    
    LICENSE_TYPES = (
        ('public', 'Public Domain'),
        ('cc-by', 'CC BY'),
        ('cc-by-sa', 'CC BY-SA'),
        ('cc-by-nc', 'CC BY-NC'),
        ('copyright', 'All Rights Reserved'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_resources'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources'
    )    
    file = models.FileField(
        upload_to=resource_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validate_pdf_file
        ],
        help_text="Only PDF files are allowed"
    )
    thumbnail = models.ImageField(
        upload_to='resource_thumbnails/',
        null=True,
        blank=True
    )
    file_size = models.PositiveIntegerField(editable=False)  # in bytes
    
    # Licensing and sharing
    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPES,
        default='cc-by'
    )
    is_free = models.BooleanField(default=True)
    allow_download = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    
    # Academic metadata
    course_code = models.CharField(max_length=20, blank=True)
    course_name = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    
    # Statistics
    downloads = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('resource')
        verbose_name_plural = _('resources')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['course_code']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    def save(self, *args, **kwargs):
        """Calculate file size before saving"""
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            while Resource.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.slug = unique_slug
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """Get the file extension in lowercase"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def download_url(self):
        """Generate download URL with tracking"""
        from django.urls import reverse
        return reverse('resource_download', kwargs={'pk': self.id})
    
    def increment_download(self):
        """Increment download counter"""
        self.downloads += 1
        self.save(update_fields=['downloads'])
    
    def increment_view(self):
        """Increment view counter"""
        self.views += 1
        self.save(update_fields=['views'])

class ResourceDownload(models.Model):
    """Track detailed download information"""
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='download_history'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('resource download')
        verbose_name_plural = _('resource downloads')
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"Download of {self.resource.title} at {self.downloaded_at}"

class ResourceComment(models.Model):
    """Comments on resources"""
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resource_comments'
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('resource comment')
        verbose_name_plural = _('resource comments')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.email} on {self.resource.title}"

class ResourceRating(models.Model):
    """Ratings for resources"""
    RATING_CHOICES = [
        (1, '★☆☆☆☆ - Poor'),
        (2, '★★☆☆☆ - Fair'),
        (3, '★★★☆☆ - Good'),
        (4, '★★★★☆ - Very Good'),
        (5, '★★★★★ - Excellent'),
    ]
    
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resource_ratings'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('resource rating')
        verbose_name_plural = _('resource ratings')
        unique_together = ('resource', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_rating_display()} by {self.user.email}"
    
    @property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
