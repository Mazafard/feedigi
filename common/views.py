from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from common import errors
from common.models import PageNumberPagination
from common.response import Response, ErrorResponse


class BaseApiView(APIView):
    pass


class BaseViewSet(ViewSetMixin, BaseApiView):
    queryset = None
    serializer_class = None
    single_serializer_class = None
    url_params = []

    @property
    def _single_serializer_class(self):
        return self.single_serializer_class if self.single_serializer_class \
            else self.serializer_class

    def has_update_permission(self, obj, request):
        return True

    def has_delete_permission(self, obj, request):
        return True

    def get_queryset(self, request):
        return self.queryset

    def list(self, request):
        objects = self.get_queryset(request).all()
        return Response(data=self.serializer_class(
            objects,
            many=True,
            context=self.get_context(request)
        ).data)

    def create(self, request):
        serializer = self._single_serializer_class(data=request.data,
                                                   context=self.get_context(request))
        if not serializer.is_valid():
            return self.data_not_valid(request, serializer.errors)

        a=serializer.save(**self.create_default_params(request))
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        obj = self.get_queryset(request).filter(pk=pk).first()
        if not obj:
            return self.not_found(request)

        return Response(
            data=self._single_serializer_class(obj,
                                               context=self.get_context(request)).data)

    def update(self, request, pk):
        obj = self.get_queryset(request).filter(pk=pk).first()
        if not obj:
            return self.not_found(request)

        if not self.has_update_permission(obj, request):
            return ErrorResponse(errors.YOU_CANNOT_UPDATE_THIS_OBJECT_AT_THIS_TIME)

        serializer = self._single_serializer_class(instance=obj, data=request.data,
                                                   context=self.get_context(request))
        if not serializer.is_valid():
            return self.data_not_valid(request, serializer.errors)

        serializer.save()
        return Response(data=serializer.data)

    def delete(self, request, pk):
        obj = self.get_queryset(request).filter(pk=pk).first()
        if not obj:
            return self.not_found(request)

        if not self.has_delete_permission(obj, request):
            return self.no_delete_permission(request)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def dispatch(self, request, *args, **kwargs):
        url_params = {}
        for param in self.url_params:
            if param in kwargs:
                url_params[param] = kwargs.pop(param)
        request.url_params = url_params
        return super().dispatch(request, *args, **kwargs)

    def create_default_params(self, request):
        return {}

    def additional_context_params(self, request):
        return {}

    def get_context(self, request):
        context = {'request': request}
        context.update(self.additional_context_params(request))
        return context

    def not_found(self, request):
        return ErrorResponse(errors.THE_REQUESTED_DATA_IS_NOT_FOUND)

    def no_delete_permission(self, request):
        return ErrorResponse(errors.YOU_CANNOT_DELETE_THIS_OBJECT_AT_THIS_TIME)

    def data_not_valid(self, request, data_errors):
        return ErrorResponse(errors.USER_DATA_INPUT_IS_NOT_VALID,
                             errors=data_errors)


class PaginatedViewSet(BaseViewSet):
    page_size = 20

    def list(self, request):
        objects = self.get_queryset(request).all()
        paginated = PageNumberPagination(objects, request, page_size=self.page_size)
        return Response(
            data=self.serializer_class(
                paginated.get_result(),
                many=True,
                context=self.get_context(request)
            ).data, headers=paginated.get_pagination_headers())
