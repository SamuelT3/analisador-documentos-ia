# Analisador de Documentos com IA

Projeto desenvolvido para um desafio técnico.

A aplicação recebe um arquivo PDF e uma pergunta em linguagem natural, envia o documento para a API da OpenAI e retorna uma resposta estruturada em JSON.

## Funcionalidades

- Recebe um arquivo PDF local como entrada
- Recebe uma pergunta em linguagem natural
- Envia o PDF para a API da OpenAI
- Analisa o documento com auxílio de IA
- Retorna uma resposta em JSON válido
- Gera uma resposta em Markdown no campo `text`
- Identifica o documento analisado no campo `source`
- Retorna exatamente 3 perguntas de acompanhamento no campo `suggestions`
- Possui estimativa opcional de custo da chamada

## Tecnologias utilizadas

- Python
- OpenAI API
- python-dotenv

## Modelo escolhido

O modelo escolhido foi `gpt-4.1-mini`.

A escolha foi feita por oferecer bom equilíbrio entre custo, velocidade e qualidade para análise de documentos. Além disso, o modelo é adequado para uso com a Responses API da OpenAI e permite a geração de respostas estruturadas em JSON Schema.

## Estrutura do projeto

```text
analisador-documentos-ia/
├── Analisador_Documentos.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Formato da resposta

A aplicação retorna obrigatoriamente um JSON no seguinte formato:

```json
{
  "type": "text",
  "text": "<resposta em Markdown>",
  "source": "<nome do documento ou N/A>",
  "suggestions": [
    "<pergunta 1>",
    "<pergunta 2>",
    "<pergunta 3>"
  ]
}
```

## Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

- Python 3.9 ou superior
- Uma API key da OpenAI
- Permissão da API key para envio de arquivos

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd analisador-documentos-ia
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar ambiente virtual

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar variável de ambiente

Crie um arquivo `.env` na raiz do projeto com base no arquivo `.env.example`.

Conteúdo do arquivo `.env`:

```env
OPENAI_API_KEY=sua_chave_aqui
```

Importante: o arquivo `.env` não deve ser enviado ao GitHub.

### 6. Executar a aplicação

Exemplo usando um PDF na mesma pasta do projeto:

```bash
python .\Analisador_Documentos.py --pdf .\relatorio.pdf --pergunta "Quais são os principais pontos do documento?"
```

Exemplo usando um PDF em outro diretório:

```bash
python .\Analisador_Documentos.py --pdf "C:\Users\SeuUsuario\Downloads\Desafio_Tecnico.pdf" --pergunta "Quais são os principais pontos do documento?"
```

Também é possível usar `--question` no lugar de `--pergunta`:

```bash
python .\Analisador_Documentos.py --pdf .\relatorio.pdf --question "Quais são os principais pontos do documento?"
```

### 7. Executar com estimativa de custo

```bash
python .\Analisador_Documentos.py --pdf .\relatorio.pdf --pergunta "Quais são os principais pontos do documento?" --mostrar-custo
```

## Exemplo de saída

```json
{
  "type": "text",
  "text": "# Principais pontos do documento\n\n- **Resumo:** o documento apresenta informações relevantes para análise.\n- **Ponto de atenção:** existem dados que podem apoiar decisões de negócio.\n- **Conclusão:** a análise permite identificar oportunidades e possíveis riscos.",
  "source": "relatorio.pdf",
  "suggestions": [
    "Quais são os principais riscos apresentados no documento?",
    "Quais indicadores merecem mais atenção?",
    "Quais ações podem ser tomadas com base nessa análise?"
  ]
}
```

## Estimativa de custo

A aplicação possui uma opção para estimar o custo da chamada com base na quantidade de tokens de entrada e saída retornados pela API.

A fórmula utilizada é:

```text
custo = (tokens_entrada / 1.000.000 * preço_entrada) + (tokens_saida / 1.000.000 * preço_saida)
```

Os valores utilizados estão definidos diretamente no código por meio das constantes:

```text
PRECO_ENTRADA_POR_1M_TOKENS
PRECO_SAIDA_POR_1M_TOKENS
```

A estimativa de custo é exibida no `stderr`, para não interferir na saída principal do programa, que deve ser somente o JSON final.

## Segurança

A chave da API deve ser armazenada no arquivo `.env`.

O arquivo `.env` está listado no `.gitignore` e não deve ser enviado ao GitHub.

O arquivo `.env.example` é disponibilizado apenas como modelo para configuração.

## Permissões da API

Para executar corretamente esta solução, a API key precisa ter permissão para envio de arquivos.

Caso ocorra o erro abaixo:

```text
Missing scopes: api.files.write
```

significa que a chave utilizada não possui permissão para upload de arquivos.

Nesse caso, é necessário utilizar uma API key com permissão adequada para arquivos ou solicitar ao responsável pelo desafio uma nova chave com essa permissão.

## Considerações finais

Esta solução foi construída com foco em simplicidade, clareza e aderência aos requisitos do desafio técnico.

O projeto recebe um PDF, envia o documento para análise com IA e retorna uma resposta estruturada, garantindo que a saída final seja um JSON válido e parseável.
