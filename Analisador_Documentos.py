import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


MODELO = "gpt-4.1-mini"

PRECO_ENTRADA_POR_1M_TOKENS = 0.40
PRECO_SAIDA_POR_1M_TOKENS = 1.60


FORMATO_RESPOSTA = {
    "type": "json_schema",
    "name": "analise_documento",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["text"],
                "description": "Tipo da resposta. Deve ser sempre text."
            },
            "text": {
                "type": "string",
                "description": "Resposta em Markdown válido, com títulos, listas e destaques."
            },
            "source": {
                "type": "string",
                "description": "Nome do documento analisado ou N/A."
            },
            "suggestions": {
                "type": "array",
                "description": "Exatamente 3 perguntas de acompanhamento relevantes.",
                "minItems": 3,
                "maxItems": 3,
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "type",
            "text",
            "source",
            "suggestions"
        ],
        "additionalProperties": False
    }
}


def validar_caminho_pdf(caminho_pdf: str) -> Path:
    """
    Valida se o caminho informado existe, se é um arquivo e se possui extensão PDF.
    """
    caminho = Path(caminho_pdf)

    if not caminho.exists():
        raise FileNotFoundError(f"O arquivo não foi encontrado: {caminho_pdf}")

    if not caminho.is_file():
        raise ValueError(f"O caminho informado não é um arquivo: {caminho_pdf}")

    if caminho.suffix.lower() != ".pdf":
        raise ValueError("O arquivo precisa ser um PDF.")

    return caminho


def enviar_pdf_para_openai(cliente: OpenAI, caminho_pdf: Path):
    """
    Envia o PDF para a OpenAI e retorna o objeto do arquivo enviado.
    """
    with caminho_pdf.open("rb") as arquivo:
        arquivo_enviado = cliente.files.create(
            file=arquivo,
            purpose="user_data"
        )

    return arquivo_enviado


def montar_prompt(pergunta: str, nome_documento: str) -> str:
    """
    Monta o prompt com as instruções para análise do documento.
    """
    return f"""
Você é um assistente especializado em análise de documentos para BI e negócios.

Analise o PDF enviado e responda à pergunta do usuário.

Documento analisado: {nome_documento}

Pergunta do usuário:
{pergunta}

Regras obrigatórias:
- Responda em português do Brasil.
- O campo "text" deve conter Markdown válido.
- Dentro do campo "text", use título, listas e destaques em negrito.
- Seja objetivo, claro e útil para um analista de negócio.
- Não invente informações que não estejam no documento.
- Se o documento não tiver informação suficiente para responder, diga isso claramente.
- O campo "source" deve conter o nome do documento analisado.
- O campo "suggestions" deve conter exatamente 3 perguntas de acompanhamento relevantes.
- A resposta final deve seguir exatamente o formato JSON solicitado.
"""


def analisar_documento(
    cliente: OpenAI,
    id_arquivo: str,
    pergunta: str,
    nome_documento: str
):
    """
    Envia o PDF e a pergunta para o modelo da OpenAI.
    """
    prompt = montar_prompt(
        pergunta=pergunta,
        nome_documento=nome_documento
    )

    resposta = cliente.responses.create(
        model=MODELO,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": id_arquivo
                    },
                    {
                        "type": "input_text",
                        "text": prompt
                    }
                ]
            }
        ],
        text={
            "format": FORMATO_RESPOSTA
        }
    )

    return resposta


def estimar_custo(resposta) -> dict:
    """
    Estima o custo da chamada com base nos tokens usados.
    """
    uso = getattr(resposta, "usage", None)

    if uso is None:
        return {
            "tokens_entrada": 0,
            "tokens_saida": 0,
            "custo_estimado_usd": 0
        }

    tokens_entrada = getattr(uso, "input_tokens", 0) or 0
    tokens_saida = getattr(uso, "output_tokens", 0) or 0

    custo_entrada = (tokens_entrada / 1_000_000) * PRECO_ENTRADA_POR_1M_TOKENS
    custo_saida = (tokens_saida / 1_000_000) * PRECO_SAIDA_POR_1M_TOKENS
    custo_total = custo_entrada + custo_saida

    return {
        "tokens_entrada": tokens_entrada,
        "tokens_saida": tokens_saida,
        "custo_estimado_usd": round(custo_total, 6)
    }


def validar_json_final(json_resposta: dict) -> dict:
    """
    Garante que o JSON final tenha exatamente os campos exigidos pelo desafio.
    """
    campos_obrigatorios = ["type", "text", "source", "suggestions"]

    for campo in campos_obrigatorios:
        if campo not in json_resposta:
            raise ValueError(f"O campo obrigatório '{campo}' não foi retornado pela IA.")

    if json_resposta["type"] != "text":
        raise ValueError('O campo "type" deve ser obrigatoriamente "text".')

    if not isinstance(json_resposta["text"], str):
        raise ValueError('O campo "text" deve ser uma string.')

    if not isinstance(json_resposta["source"], str):
        raise ValueError('O campo "source" deve ser uma string.')

    if not isinstance(json_resposta["suggestions"], list):
        raise ValueError('O campo "suggestions" deve ser uma lista.')

    if len(json_resposta["suggestions"]) != 3:
        raise ValueError('O campo "suggestions" deve conter exatamente 3 perguntas.')

    return {
        "type": json_resposta["type"],
        "text": json_resposta["text"],
        "source": json_resposta["source"],
        "suggestions": json_resposta["suggestions"]
    }


def executar_programa():
    """
    Função principal do programa.
    """
    load_dotenv()

    analisador_argumentos = argparse.ArgumentParser(
        description="Analisador de documentos PDF com IA"
    )

    analisador_argumentos.add_argument(
        "--pdf",
        required=True,
        help="Caminho local do arquivo PDF"
    )

    analisador_argumentos.add_argument(
        "--pergunta",
        "--question",
        dest="pergunta",
        required=True,
        help="Pergunta em linguagem natural sobre o documento"
    )

    analisador_argumentos.add_argument(
        "--mostrar-custo",
        "--show-cost",
        dest="mostrar_custo",
        action="store_true",
        help="Mostra a estimativa de custo no stderr"
    )

    argumentos = analisador_argumentos.parse_args()

    chave_api = os.getenv("OPENAI_API_KEY")

    if not chave_api:
        print(
            "Erro: OPENAI_API_KEY não encontrada. Crie um arquivo .env com sua chave.",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        cliente = OpenAI(api_key=chave_api)

        caminho_pdf = validar_caminho_pdf(argumentos.pdf)

        arquivo_enviado = enviar_pdf_para_openai(
            cliente=cliente,
            caminho_pdf=caminho_pdf
        )

        resposta = analisar_documento(
            cliente=cliente,
            id_arquivo=arquivo_enviado.id,
            pergunta=argumentos.pergunta,
            nome_documento=caminho_pdf.name
        )

        texto_resposta = resposta.output_text.strip()

        json_resposta = json.loads(texto_resposta)

        json_final = validar_json_final(json_resposta)

        if argumentos.mostrar_custo:
            custo = estimar_custo(resposta)
            print(
                f"Estimativa de custo: {json.dumps(custo, ensure_ascii=False)}",
                file=sys.stderr
            )

        print(json.dumps(json_final, ensure_ascii=False, indent=2))

    except Exception as erro:
        print(f"Erro ao executar análise: {erro}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    executar_programa()