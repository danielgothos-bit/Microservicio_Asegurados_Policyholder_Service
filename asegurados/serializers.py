from rest_framework import serializers

from .models import Asegurado, DocKyc


class DocKycSerializer(serializers.ModelSerializer):
    id_asegurado = serializers.UUIDField(source="asegurado_id", read_only=True)

    class Meta:
        model = DocKyc
        fields = ["id_doc", "id_asegurado", "tipo_documento", "documento_url", "verificado_en"]
        read_only_fields = ["id_doc", "verificado_en"]


class AseguradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asegurado
        fields = [
            "id_asegurado",
            "nombre",
            "apellido",
            "national_id",
            "email",
            "telefono",
            "direccion",
            "kyc_status",
            "fecha_registro",
        ]
        read_only_fields = ["id_asegurado", "kyc_status", "fecha_registro"]


class ContactoSerializer(serializers.ModelSerializer):
    """Solo los datos de contacto se pueden actualizar."""

    class Meta:
        model = Asegurado
        fields = ["email", "telefono", "direccion"]


class KycEstadoSerializer(serializers.Serializer):
    kyc_status = serializers.ChoiceField(choices=[Asegurado.VERIFICADO, Asegurado.RECHAZADO])
