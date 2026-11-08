"""API REST de mensagens com validacao e documentacao OpenAPI."""

from typing import Annotated

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, StringConstraints


class MensagemEntrada(BaseModel):
    texto: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, strict=True)]


class Mensagem(BaseModel):
    id: int
    texto: str


def create_app():
    app = FastAPI(title="Messages API", version="1.0.0",
                  description="API REST para gerenciar mensagens em memoria.")
    mensagens = {1: Mensagem(id=1, texto="Hello World!")}
    proximo_id = 2

    def buscar_mensagem(mensagem_id: int) -> Mensagem:
        if mensagem_id not in mensagens:
            raise HTTPException(status_code=404, detail="Mensagem nao encontrada.")
        return mensagens[mensagem_id]

    @app.get("/", tags=["Inicio"])
    async def hello_world() -> dict[str, str]:
        return {"mensagem": "Hello World!"}

    @app.get("/api/mensagens", response_model=list[Mensagem], tags=["Mensagens"])
    async def listar_mensagens():
        return list(mensagens.values())

    @app.get("/api/mensagens/{mensagem_id}", response_model=Mensagem,
             tags=["Mensagens"], responses={404: {"description": "Mensagem inexistente"}})
    async def consultar_mensagem(mensagem_id: int):
        return buscar_mensagem(mensagem_id)

    @app.post("/api/mensagens", response_model=Mensagem,
              status_code=status.HTTP_201_CREATED, tags=["Mensagens"])
    async def criar_mensagem(dados: MensagemEntrada, response: Response):
        nonlocal proximo_id
        mensagem = Mensagem(id=proximo_id, texto=dados.texto)
        mensagens[proximo_id] = mensagem
        proximo_id += 1
        response.headers["Location"] = f"/api/mensagens/{mensagem.id}"
        return mensagem

    @app.put("/api/mensagens/{mensagem_id}", response_model=Mensagem,
             tags=["Mensagens"], responses={404: {"description": "Mensagem inexistente"}})
    async def atualizar_mensagem(mensagem_id: int, dados: MensagemEntrada):
        buscar_mensagem(mensagem_id)
        mensagem = Mensagem(id=mensagem_id, texto=dados.texto)
        mensagens[mensagem_id] = mensagem
        return mensagem

    @app.delete("/api/mensagens/{mensagem_id}", status_code=status.HTTP_204_NO_CONTENT,
                response_class=Response, tags=["Mensagens"],
                responses={404: {"description": "Mensagem inexistente"}})
    async def excluir_mensagem(mensagem_id: int):
        buscar_mensagem(mensagem_id)
        del mensagens[mensagem_id]
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
