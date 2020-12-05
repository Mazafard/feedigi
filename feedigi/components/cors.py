from corsheaders.defaults import default_headers

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = default_headers + (
    "X-Pagination-Total-Count",
    "X-Pagination-Page-Count",
    "X-Pagination-Current-Page",
    "X-Pagination-Per-Page",
    "X-Pagination-Sortable-Fields",
    "X-Pagination-Filterable-Fields",
    "Link",
    "x-locale",
    "x-currency"
)
FILE_UPLOAD_PERMISSIONS = 0o644
