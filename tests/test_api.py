"""Testes do contrato HTTP com a aplicacao real e dados isolados."""

import json
import unittest

from fastapi.testclient import TestClient

from main import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())
        self.addCleanup(self.client.close)

    def test_raiz_retorna_hello_world_em_json(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), {"mensagem": "Hello World!"})

    def test_lista_inicial_contem_mensagem(self):
        resposta = self.client.get("/api/mensagens")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json(), [{"id": 1, "texto": "Hello World!"}])

    def test_criacao_pode_ser_consultada_pelo_location(self):
        resposta = self.client.post("/api/mensagens", json={"texto": "Ola, FastAPI!"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json(), {"id": 2, "texto": "Ola, FastAPI!"})
        consulta = self.client.get(resposta.headers["Location"])
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json(), resposta.json())

    def test_atualizacao_persiste_na_consulta(self):
        resposta = self.client.put("/api/mensagens/1", json={"texto": "Mensagem atualizada"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.client.get("/api/mensagens/1").json(),
                         {"id": 1, "texto": "Mensagem atualizada"})

    def test_exclusao_remove_mensagem_e_retorna_corpo_vazio(self):
        resposta = self.client.delete("/api/mensagens/1")
        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(resposta.content, b"")
        self.assertEqual(self.client.get("/api/mensagens/1").status_code, 404)
        self.assertEqual(self.client.get("/api/mensagens").json(), [])

    def test_ids_nao_sao_reutilizados_apos_exclusao(self):
        self.client.delete("/api/mensagens/1")
        resposta = self.client.post("/api/mensagens", json={"texto": "Nova mensagem"})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["id"], 2)

    def test_recurso_inexistente_retorna_404_em_json(self):
        for metodo in ("GET", "PUT", "DELETE"):
            with self.subTest(metodo=metodo):
                resposta = self.client.request(metodo, "/api/mensagens/999",
                                               json={"texto": "Ola"})
                self.assertEqual(resposta.status_code, 404)
                self.assertIn("detail", resposta.json())

    def test_post_e_put_rejeitam_texto_invalido_sem_alterar_dados(self):
        for metodo, url in (("POST", "/api/mensagens"), ("PUT", "/api/mensagens/1")):
            for corpo in ({}, {"texto": ""}, {"texto": "   "}, {"texto": 42},
                          {"texto": None}, [], ["Ola"], "Ola", None):
                with self.subTest(metodo=metodo, corpo=corpo):
                    resposta = self.client.request(metodo, url,
                                                   content=json.dumps(corpo),
                                                   headers={"Content-Type": "application/json"})
                    self.assertEqual(resposta.status_code, 422)
                    self.assertIn("detail", resposta.json())
        self.assertEqual(self.client.get("/api/mensagens").json(),
                         [{"id": 1, "texto": "Hello World!"}])

    def test_json_malformado_retorna_422(self):
        resposta = self.client.post("/api/mensagens", content='{"texto":',
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(resposta.status_code, 422)
        self.assertIn("detail", resposta.json())

    def test_texto_puro_retorna_422(self):
        resposta = self.client.post("/api/mensagens", content="Ola!",
                                    headers={"Content-Type": "text/plain"})
        self.assertEqual(resposta.status_code, 422)
        self.assertIn("detail", resposta.json())

    def test_texto_tem_espacos_externos_removidos(self):
        resposta = self.client.post("/api/mensagens", json={"texto": "  Ola!  "})
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json()["texto"], "Ola!")

    def test_openapi_descreve_as_operacoes_e_seus_status(self):
        resposta = self.client.get("/openapi.json")
        self.assertEqual(resposta.status_code, 200)
        caminhos = resposta.json()["paths"]
        for url, metodo, status in (("/", "get", "200"),
                                    ("/api/mensagens", "get", "200"),
                                    ("/api/mensagens", "post", "201"),
                                    ("/api/mensagens/{mensagem_id}", "get", "200"),
                                    ("/api/mensagens/{mensagem_id}", "put", "200"),
                                    ("/api/mensagens/{mensagem_id}", "delete", "204")):
            with self.subTest(url=url, metodo=metodo):
                self.assertIn(status, caminhos[url][metodo]["responses"])


if __name__ == "__main__":
    unittest.main()
