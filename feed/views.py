from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from common.auth import CustomTokenAuthentication
from common.response import Response
from common.views import PaginatedViewSet
from feed.models import Post, Source
from feed.serializers import SourceSerializer, PostSerializer


class SourceApiView(PaginatedViewSet):
    serializer_class = SourceSerializer

    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, request):
        return request.user.sources

    def create_default_params(self, request):
        return {
            'user': request.user
        }


class PostApiView(PaginatedViewSet):
    serializer_class = PostSerializer

    authentication_classes = (CustomTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    url_params = ['pk']

    def get_queryset(self, request):
        source = Source.get_by_pk(request.url_params['pk'])
        if not source:
            raise NotFound('The requested Source is not found')
        return Post.get_all_by_source_and_user(
            source=source,
            user=request.user
        )

    def create_default_params(self, request):
        source = Source.get_by_pk(request.url_params['pk'])
        if not source:
            raise NotFound('The requested Source is not found')
        return {
            'source': source
        }

    def additional_context_params(self, request):
        source = Source.get_by_pk(request.url_params['pk'])
        if not source:
            raise NotFound('The requested Source is not found')
        return {
            'source': source
        }

    def retrieve(self, request, post_id):
        return super().retrieve(request, post_id)

    def update(self, request, post_id):
        return super().update(request, post_id)

    def delete(self, request, post_id):
        return super().delete(request, post_id)

    def like(self, request, post_id):
        obj = self.get_queryset(request).filter(pk=post_id).first()  # type: Post
        if not obj:
            return self.not_found(request)
        obj.like()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def dislike(self, request, post_id):
        obj = self.get_queryset(request).filter(pk=post_id).first() # type: Post
        if not obj:
            return self.not_found(request)

        if not self.has_delete_permission(obj, request):
            return self.no_delete_permission(request)

        obj.unlike()
        return Response(status=status.HTTP_204_NO_CONTENT)
