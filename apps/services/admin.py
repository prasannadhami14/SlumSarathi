from django.contrib import admin
from .models import ServiceCategory, Service, ServiceImage, ServiceRequest, ServiceReview

class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'service_type', 'pricing_model', 'display_price', 'is_available')
    list_filter = ('service_type', 'pricing_model', 'is_available', 'category')
    search_fields = ('title', 'description', 'provider__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceImageInline]
    readonly_fields = ('views',)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('service', 'requester', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('service__title', 'requester__email')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['accept_requests', 'reject_requests']

    def accept_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.accept()
    accept_requests.short_description = "Accept selected requests"

    def reject_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.reject()
    reject_requests.short_description = "Reject selected requests"

admin.site.register(ServiceCategory)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceRequest, ServiceRequestAdmin)
admin.site.register(ServiceReview)