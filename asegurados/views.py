from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from comun.eventos import publicar

from .models import Asegurado
from .serializers import (
    AseguradoSerializer,
    ContactoSerializer,
    DocKycSerializer,
    KycEstadoSerializer,
)


@api_view(["GET", "POST"])
def asegurados(request):
    if request.method == "GET":
        qs = Asegurado.objects.order_by("-fecha_registro")
        if request.query_params.get("national_id"):
            qs = qs.filter(national_id=request.query_params["national_id"])
        return Response(AseguradoSerializer(qs, many=True).data)

    serializer = AseguradoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    asegurado = serializer.save()

    publicar("policyholder.created", {
        "id_asegurado": asegurado.id_asegurado,
        "nombre": asegurado.nombre,
        "apellido": asegurado.apellido,
        "email": asegurado.email,
    })

    return Response(AseguradoSerializer(asegurado).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT"])
def asegurado_detalle(request, id):
    asegurado = get_object_or_404(Asegurado, id_asegurado=id)

    if request.method == "GET":
        return Response(AseguradoSerializer(asegurado).data)

    serializer = ContactoSerializer(asegurado, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(AseguradoSerializer(asegurado).data)


@api_view(["GET", "PUT"])
def asegurado_kyc(request, id):
    asegurado = get_object_or_404(Asegurado, id_asegurado=id)

    if request.method == "PUT":
        serializer = KycEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asegurado.kyc_status = serializer.validated_data["kyc_status"]
        asegurado.save(update_fields=["kyc_status"])
        asegurado.documentos_kyc.filter(verificado_en__isnull=True).update(verificado_en=timezone.now())

        publicar("policyholder.kyc_updated", {
            "id_asegurado": asegurado.id_asegurado,
            "kyc_status": asegurado.kyc_status,
        })

    return Response({
        "id_asegurado": asegurado.id_asegurado,
        "kyc_status": asegurado.kyc_status,
        "documentos": DocKycSerializer(asegurado.documentos_kyc.all(), many=True).data,
    })


@api_view(["POST"])
def asegurado_kyc_documentos(request, id):
    asegurado = get_object_or_404(Asegurado, id_asegurado=id)
    serializer = DocKycSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    doc = serializer.save(asegurado=asegurado)
    return Response(DocKycSerializer(doc).data, status=status.HTTP_201_CREATED)
