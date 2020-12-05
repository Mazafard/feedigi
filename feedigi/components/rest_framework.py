from corsheaders.defaults import default_headers

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    "X-Pagination-Total-Count",
    "X-Pagination-Page-Count",
    "X-Pagination-Current-Page",
    "X-Pagination-Per-Page",
    "X-Pagination-Sortable-Fields",
    "X-Pagination-Filterable-Fields",
    "X-Pagination-Searchable-Fields",
    "Link",
    "x-locale",
    "x-currency",
    "Accepted-language",
)

CORS_EXPOSE_HEADERS = (
    "X-Pagination-Total-Count",
    "X-Pagination-Page-Count",
    "X-Pagination-Current-Page",
    "X-Pagination-Per-Page",
    "X-Pagination-Sortable-Fields",
    "X-Pagination-Filterable-Fields",
    "X-Pagination-Searchable-Fields",
    "Link",
    "x-locale",
    "x-currency",
    "Accepted-language",
)
