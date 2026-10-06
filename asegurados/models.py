import uuid

from django.db import models
from django.db.models import Q


class Asegurado(models.Model):
    PENDIENTE = "pendiente"
    VERIFICADO = "verificado"
    RECHAZADO = "rechazado"

    KYC_CHOICES = [
        (PENDIENTE, "Pendiente"),
        (VERIFICADO, "Verificado"),
        (RECHAZADO, "Rechazado"),
    ]

    id_asegurado = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    national_id = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.TextField(blank=True)
    kyc_status = models.CharField(max_length=20, choices=KYC_CHOICES, default=PENDIENTE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "asegurado"
        indexes = [
            models.Index(fields=["national_id"], name="idx_asegurado_national_id"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(kyc_status__in=["pendiente", "verificado", "rechazado"]),
                name="chk_asegurado_kyc_status",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.national_id})"


class DocKyc(models.Model):
    """Documentos de verificación de identidad (KYC) aportados por un asegurado."""

    id_doc = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asegurado = models.ForeignKey(
        Asegurado, on_delete=models.CASCADE, related_name="documentos_kyc", db_column="id_asegurado"
    )
    tipo_documento = models.CharField(max_length=50)
    documento_url = models.TextField()
    verificado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "doc_kyc"
        indexes = [
            models.Index(fields=["asegurado"], name="idx_doc_kyc_asegurado"),
        ]

    def __str__(self):
        return f"{self.tipo_documento} - {self.asegurado_id}"
