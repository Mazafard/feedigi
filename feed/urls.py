from django.urls import path, include

from feed import views

urlpatterns = [
    path('source/', include([
        path('', views.SourceApiView.as_view({
            'get': 'list',
            'post': 'create',

        }), name='source_list'
             ),
        path('<int:pk>/', include([
            path('', views.SourceApiView.as_view({
                'get': 'retrieve',
                'put': 'update',
                'delete': 'delete',

            }), name='source_detail'
                 ),
            path('post/', include([
                path('', views.PostApiView.as_view({
                    'get': 'list',
                    'post': 'create',
                }), name='post_list'
                     ),
                path('<int:post_id>/', include([
                    path('', views.PostApiView.as_view({
                        'get': 'retrieve',
                        'put': 'update',
                        'delete': 'delete',
                    }), name='post_detail'
                         ),
                    path('favorite/', views.PostApiView.as_view({

                        'patch': 'like',
                        'delete': 'dislike',
                    }), name='post_favorite'
                         ),

                ])),

            ])),
        ])),
    ])),
]

#     path('login/', views.UserLoginApiView.as_view()),
#     path('profile/', views.ProfileApiView.as_view()),
#     path('reset-password/', views.ResetPasswordApiView.as_view()),
#     path('change-password/', views.ChangePasswordApiView.as_view()),
#     path('verify-email/<verification_text>', views.VerifyEmailApiView.as_view()),
#     path('verify-password/<verification_text>', views.VerifyPasswordApiView.as_view()),
