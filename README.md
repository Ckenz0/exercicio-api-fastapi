# FastAPI Messages API

API REST para gerenciar mensagens com FastAPI, validação de dados com Pydantic e servidor ASGI Uvicorn. As respostas usam JSON. Os dados são armazenados em memória durante a execução.

## Instalação

Com Python 3.12 instalado, abra o terminal na pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para instalar também as dependências de testes:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Execução com Uvicorn

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

`main:app` indica o arquivo `main.py` e a aplicação `app` definida nele. Pare o servidor com `Ctrl+C`. Durante o desenvolvimento, é possível adicionar `--reload` para reiniciar o processo após salvar alterações; isso também reinicia os dados em memória.

No VS Code, selecione o interpretador `.venv/Scripts/python.exe`, escolha a configuração **FastAPI - Uvicorn** em **Executar e Depurar** e pressione **F5**.

| Endereço | Conteúdo |
| --- | --- |
| <http://127.0.0.1:8000/> | Mensagem de boas-vindas em JSON |
| <http://127.0.0.1:8000/api/mensagens> | Lista de mensagens |
| <http://127.0.0.1:8000/docs> | Documentação interativa Swagger UI |
| <http://127.0.0.1:8000/redoc> | Documentação ReDoc |
| <http://127.0.0.1:8000/openapi.json> | Contrato OpenAPI |

## Endpoints

| Método | Caminho | Operação | Sucesso |
| --- | --- | --- | --- |
| GET | `/` | Consultar a mensagem de boas-vindas | 200 |
| GET | `/api/mensagens` | Listar mensagens | 200 |
| GET | `/api/mensagens/{id}` | Consultar uma mensagem | 200 |
| POST | `/api/mensagens` | Criar mensagem | 201 |
| PUT | `/api/mensagens/{id}` | Atualizar o texto | 200 |
| DELETE | `/api/mensagens/{id}` | Excluir mensagem | 204 |

POST e PUT recebem `Content-Type: application/json` e um objeto como:

```json
{"texto": "Olá, FastAPI!"}
```

Uma criação retorna o recurso e seu ID:

```json
{"id": 2, "texto": "Olá, FastAPI!"}
```

O cabeçalho `Location` identifica a URL do recurso criado. DELETE retorna corpo vazio. O servidor inicia com a mensagem `{"id": 1, "texto": "Hello World!"}`.

O campo `texto` é obrigatório, deve ser uma string e não pode ficar vazio após remover os espaços externos. Campos adicionais são ignorados. Recurso inexistente retorna **404** com `{"detail": "Mensagem nao encontrada."}`. Entradas inválidas retornam **422** com os detalhes da validação, incluindo JSON malformado, campo ausente ou corpo enviado como texto puro.

Reiniciar o processo restaura a mensagem inicial. Execute uma instância local, sem múltiplos workers, pois cada processo mantém seus próprios dados.

## Postman

1. Mantenha o Uvicorn em execução.
2. Importe `postman/messages-api.postman_collection.json`.
3. Abra **Messages API - FastAPI** e confira a variável `baseUrl`: `http://127.0.0.1:8000`.
4. Execute as 11 requisições na ordem numerada, com uma iteração.

São 23 verificações. A criação salva o ID em `mensagemId`; as requisições seguintes consultam, alteram e excluem a mensagem criada. A mensagem inicial é preservada. Os status 404 e 422 nos casos de erro são esperados. Se o servidor reiniciar durante a sequência, execute novamente a criação.

Com o Postman CLI instalado:

```powershell
postman collection run postman/messages-api.postman_collection.json --no-report-events
```

O endereço `127.0.0.1` se refere à máquina que executa a requisição. Para testar em outro computador, execute a API nesse computador ou altere `baseUrl` para um servidor acessível.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes verificam operações de leitura e escrita, IDs, validação de entradas, respostas HTTP e o contrato OpenAPI. Cada teste cria uma aplicação com dados isolados.
