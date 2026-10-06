from unittest import mock

from rest_framework.test import APITestCase

DATOS = {
    "nombre": "Ana",
    "apellido": "Gómez",
    "national_id": "1020304050",
    "email": "ana@example.com",
    "telefono": "3001234567",
    "direccion": "Calle 1 # 2-3, Medellín",
}


@mock.patch("asegurados.views.publicar")
class AseguradosTests(APITestCase):
    def crear(self):
        return self.client.post("/api/v1/asegurados", DATOS, format="json")

    def test_registrar_y_consultar(self, publicar):
        resp = self.crear()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["kyc_status"], "pendiente")
        self.assertEqual(publicar.call_args[0][0], "policyholder.created")

        resp = self.client.get(f"/api/v1/asegurados/{resp.data['id_asegurado']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["email"], "ana@example.com")

    def test_national_id_unico(self, publicar):
        self.crear()
        resp = self.client.post("/api/v1/asegurados", dict(DATOS, email="otra@example.com"), format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["code"], "VALIDATION_ERROR")

    def test_actualizar_contacto_no_cambia_identidad(self, publicar):
        id = self.crear().data["id_asegurado"]
        resp = self.client.put(f"/api/v1/asegurados/{id}", {"telefono": "3110000000", "nombre": "X"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["telefono"], "3110000000")
        self.assertEqual(resp.data["nombre"], "Ana")

    def test_kyc(self, publicar):
        id = self.crear().data["id_asegurado"]
        resp = self.client.post(f"/api/v1/asegurados/{id}/kyc/documentos",
                                {"tipo_documento": "cedula", "documento_url": "https://docs/cedula.pdf"}, format="json")
        self.assertEqual(resp.status_code, 201)

        resp = self.client.put(f"/api/v1/asegurados/{id}/kyc", {"kyc_status": "verificado"}, format="json")
        self.assertEqual(resp.data["kyc_status"], "verificado")
        self.assertIsNotNone(resp.data["documentos"][0]["verificado_en"])
        self.assertEqual(publicar.call_args[0][0], "policyholder.kyc_updated")

    def test_no_existe(self, publicar):
        resp = self.client.get("/api/v1/asegurados/00000000-0000-0000-0000-000000000000")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data["code"], "NOT_FOUND")
