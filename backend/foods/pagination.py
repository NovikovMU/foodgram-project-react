from rest_framework.pagination import PageNumberPagination

class CommonResultPagination(PageNumberPagination):
    page_size = 6
