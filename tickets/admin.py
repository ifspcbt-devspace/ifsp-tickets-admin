from datetime import datetime, timedelta
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm

from .models import (
    Addresses,
    Companies,
    Enrollments,
    Events,
    EventConfigurations,
    EventsThumbnails,
    OrderItems,
    Orders,
    Payments,
    Tickets,
    TicketSale,
    Users,
)

admin.site.site_header = "Tickets IFSP Admin"
admin.site.site_title = "Administração do Site"
admin.site.index_title = "Painel Administrativo"


class EventConfigurationsForm(ModelForm):
    class Meta:
        model = EventConfigurations
        fields = ["key", "value"]


class EventConfigurationsInline(admin.TabularInline):
    model = EventConfigurations
    extra = 4
    form = EventConfigurationsForm

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)

        if obj is None:  # Novo evento
            # Lista de valores padrão
            defaults = [
                {"key": "HAS_DEFAULT_TICKET", "value": "false"},
                {"key": "DEFAULT_TICKET_ID", "value": ""},
                {
                    "key": "END_SELLING_DATE",
                    "value": (datetime.now() + timedelta(days=30)).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                },
                {
                    "key": "START_SELLING_DATE",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            ]

            class DefaultFormSet(FormSet):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    for i, form in enumerate(self.forms):
                        if i < len(defaults):
                            form.initial.update(defaults[i])

            return DefaultFormSet

        return FormSet


class EventsThumbnailsInline(admin.TabularInline):
    model = EventsThumbnails
    extra = 1


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "init_date", "end_date", "company_id")
    list_filter = ("status", "init_date", "end_date")
    search_fields = ("name", "description")
    inlines = [EventConfigurationsInline]


@admin.register(Enrollments)
class EnrollmentsAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "event_id", "status")
    list_filter = ("status", "event_id")
    search_fields = ("name", "email", "document")


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "document")


@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ("id", "order_id", "status", "amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_id", "external_id")


@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("code", "description")


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("username", "name", "email", "active", "role_id", "company_id")
    search_fields = ("username", "name", "email", "document")
    list_filter = ("active", "role_id", "company_id")


admin.site.register(Addresses)
admin.site.register(Companies)
admin.site.register(OrderItems)
admin.site.register(TicketSale)
