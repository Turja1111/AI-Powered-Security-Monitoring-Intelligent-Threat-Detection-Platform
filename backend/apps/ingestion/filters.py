import django_filters
from .models import LogEntry

class LogEntryFilter(django_filters.FilterSet):
    """Filterset class for advanced Django filtering on LogEntry objects."""
    
    start_time = django_filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="gte")
    end_time = django_filters.IsoDateTimeFilter(field_name="timestamp", lookup_expr="lte")
    source_ip = django_filters.CharFilter(field_name="source_ip", lookup_expr="exact")
    destination_ip = django_filters.CharFilter(field_name="destination_ip", lookup_expr="exact")
    protocol = django_filters.CharFilter(field_name="protocol", lookup_expr="iexact")
    label = django_filters.CharFilter(field_name="label", lookup_expr="exact")
    source = django_filters.CharFilter(field_name="source", lookup_expr="exact")

    class Meta:
        model = LogEntry
        fields = ["source_ip", "destination_ip", "protocol", "label", "source"]
