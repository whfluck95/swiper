"""swiper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from user import api as user_api
from social import api as socail_api
urlpatterns = [
    url(r'^api/user/get_vcode', user_api.get_vcode),
    url(r'^api/user/check_vcode', user_api.check_vcode),
    url(r'^api/user/get_profile', user_api.get_profile),
    url(r'^api/user/set_profile', user_api.set_profile),
    url(r'^api/user/upload_avatar', user_api.upload_avatar),

    url(r'^weibo/wb_auth', user_api.wb_auth),
    url(r'^weibo/callback', user_api.wb_callback),

    url(r'^api/social/get_rcmd_users',socail_api.get_rcmd_users),
    url(r'^api/social/like',socail_api.like),
    url(r'^api/social/superlike',socail_api.superlike),
    url(r'^api/social/dislike',socail_api.dislike),
    url(r'^api/social/rewind',socail_api.rewind),
    url(r'^api/social/who_liked_me',socail_api.who_liked_me),
    url(r'^api/social/friend_list',socail_api.friend_list),
]