"""
URLs para reportes y dashboards
"""
from django.urls import path
from .views import (
    DashboardEmpresaView,
    DashboardEmpresaPDFView,
    DashboardEmpleadoView,
    DashboardEmpleadoPDFView,
    CalcularLiquidacionView,
    LiquidacionPDFView,
)

app_name = 'reportes'

urlpatterns = [
    path('empresa/<str:empresa_id>/dashboard/', DashboardEmpresaView.as_view(), name='dashboard-empresa'),
    path('empresa/<str:empresa_id>/dashboard/pdf/', DashboardEmpresaPDFView.as_view(), name='dashboard-empresa-pdf'),
    path('empleado/<str:empleado_id>/dashboard/', DashboardEmpleadoView.as_view(), name='dashboard-empleado'),
    path('empleado/<str:empleado_id>/dashboard/pdf/', DashboardEmpleadoPDFView.as_view(), name='dashboard-empleado-pdf'),
    path('empleado/<str:empleado_id>/liquidacion/', CalcularLiquidacionView.as_view(), name='calcular-liquidacion'),
    path('empleado/<str:empleado_id>/liquidacion/pdf/', LiquidacionPDFView.as_view(), name='liquidacion-pdf'),
]
