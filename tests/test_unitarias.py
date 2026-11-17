"""Pruebas unitarias: una unidad de lógica de negocio aislada; las dependencias externas se simulan con mocks."""
from unittest import mock

from django.test import TestCase

from asegurados.serializers import AseguradoSerializer

DATOS = {"nombre": "Ana", "apellido": "Gómez", "national_id": "1020304050", "email": "ana@example.com",
         "telefono": "3001234567", "direccion": "Montería"}


class AseguradoUnitTests(TestCase):
    def test_serializer_rechaza_correo_invalido(self):
        s = AseguradoSerializer(data=dict(DATOS, email="no-es-un-correo"))
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)

    @mock.patch("asegurados.views.publicar")
    def test_verificar_kyc_publica_evento(self, publicar):
        id_aseg = self.client.post("/api/v1/asegurados", DATOS, content_type="application/json").json()["id_asegurado"]
        resp = self.client.put(f"/api/v1/asegurados/{id_aseg}/kyc", {"kyc_status": "verificado"}, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(publicar.call_args[0][0], "policyholder.kyc_updated")
