"""Prueba de integración: endpoint + lógica de negocio + base de datos funcionando juntos."""
from unittest import mock

from rest_framework.test import APITestCase

from asegurados.models import Asegurado


@mock.patch("asegurados.views.publicar")
class AseguradoIntegracionTests(APITestCase):
    def test_registrar_consultar_y_actualizar_contacto(self, publicar):
        datos = {"nombre": "Luis", "apellido": "Pérez", "national_id": "1067111222", "email": "luis@example.com",
                 "telefono": "3005556677", "direccion": "Cereté"}
        resp = self.client.post("/api/v1/asegurados", datos, format="json")
        self.assertEqual(resp.status_code, 201)
        id_aseg = resp.data["id_asegurado"]
        self.assertEqual(self.client.get(f"/api/v1/asegurados/{id_aseg}").data["national_id"], "1067111222")
        self.client.put(f"/api/v1/asegurados/{id_aseg}", {"telefono": "3119998877"}, format="json")
        self.assertEqual(Asegurado.objects.get(pk=id_aseg).telefono, "3119998877")
        self.assertEqual(self.client.post("/api/v1/asegurados", datos, format="json").status_code, 400)  # cédula repetida
