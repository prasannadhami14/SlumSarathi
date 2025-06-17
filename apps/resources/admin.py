# resources/admin.py
from django import forms
from django.contrib import admin
from .models import (
    ResourceCategory, 
    Resource, 
    ResourceDownload, 
    ResourceComment,
    ResourceRating
)
class ResourceDownloadInline(admin.TabularInline):
    model = ResourceDownload
    extra = 0
    readonly_fields = ('user', 'ip_address', 'user_agent', 'referrer', 'downloaded_at')
    can_delete = False

class ResourceCommentInline(admin.TabularInline):
    model = ResourceComment
    extra = 0
    readonly_fields = ('user', 'created_at', 'updated_at')

class ResourceRatingInline(admin.TabularInline):
    model = ResourceRating
    extra = 0
    readonly_fields = ('user', 'rating', 'created_at', 'updated_at')

class ResourceAdminForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
        return file

class ResourceAdmin(admin.ModelAdmin):
    form = ResourceAdminForm
    list_display = (
        'title', 
        'uploader', 
        'resource_type', 
        'course_code',
        'downloads',
        'is_approved',
        'is_featured'
    )
    list_filter = (
        'resource_type', 
        'is_approved',
        'is_featured',
        'category',
        'license_type'
    )
    search_fields = (
        'title', 
        'description', 
        'course_code',
        'course_name',
        'uploader__email'
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'file_size',
        'downloads',
        'views',
        'created_at',
        'updated_at'
    )
    inlines = [
        ResourceDownloadInline,
        ResourceCommentInline,
        ResourceRatingInline
    ]
    actions = ['approve_resources', 'feature_resources']

    def approve_resources(self, request, queryset):
        queryset.update(is_approved=True)
    approve_resources.short_description = "Approve selected resources"

    def feature_resources(self, request, queryset):
        queryset.update(is_featured=True)
    feature_resources.short_description = "Feature selected resources"

admin.site.register(ResourceCategory)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceComment)
admin.site.register(ResourceRating)