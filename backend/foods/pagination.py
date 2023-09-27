from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE


class CommonResultPagination(PageNumberPagination):
    page_size = PAGE_SIZE
