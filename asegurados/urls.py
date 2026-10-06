from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/asegurados", views.asegurados),
    path("api/v1/asegurados/<uuid:id>", views.asegurado_detalle),
    path("api/v1/asegurados/<uuid:id>/kyc", views.asegurado_kyc),
    path("api/v1/asegurados/<uuid:id>/kyc/documentos", views.asegurado_kyc_documentos),
]
