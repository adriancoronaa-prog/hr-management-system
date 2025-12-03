"""
URLs para integraciones
"""
from django.urls import path
from .views import (
    GoogleCalendarAuthView,
    GoogleCalendarAuthorizeView,
    GoogleCalendarCallbackView,
    GoogleCalendarStatusView,
    GoogleCalendarDisconnectView,
)

app_name = 'integraciones'

urlpatterns = [
    path('google/auth/', GoogleCalendarAuthView.as_view(), name='google_auth'),
    path('google/authorize/', GoogleCalendarAuthorizeView.as_view(), name='google_authorize'),
    path('google/callback/', GoogleCalendarCallbackView.as_view(), name='google_callback'),
    path('google/status/', GoogleCalendarStatusView.as_view(), name='google_status'),
    path('google/disconnect/', GoogleCalendarDisconnectView.as_view(), name='google_disconnect'),
]
