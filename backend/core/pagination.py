from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    """Standard page-based pagination for medium list volumes."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class CursorPaginationForLogs(CursorPagination):
    """Cursor-based pagination designed to handle massive volumes (100k+) of log events efficiently."""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200
    ordering = "-timestamp"
