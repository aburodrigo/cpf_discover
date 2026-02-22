# CPF Discover — DISCOVER v2.5

Automação simples para gerar listas de CPFs válidos e buscar possíveis associações de nomes através de buscas públicas (ex.: JusBrasil).

## Visão geral

Este repositório contém dois scripts principais:

- `gerar_cpfs.py`: gera CPFs válidos a partir de 6 dígitos centrais fornecidos pelo usuário e grava em `cpfvalido.txt`.
- `consulta_cpf.py`: automatiza buscas usando Playwright para verificar se um determinado nome aparece em páginas retornadas pela busca do CPF.

Estrutura típica do projeto:

E:/Scripts_Python/cpf_discover/
- consulta_cpf.py
- gerar_cpfs.py
- requirements.txt
- cpfvalido.txt            # gerado por `gerar_cpfs.py`
- resultados_busca.txt     # gerado por `consulta_cpf.py`
- checkpoint.json          # gerado por `consulta_cpf.py` durante execução
- README.md

## Requisitos

- Python 3.7+
- Dependências: listadas em `requirements.txt` (usa `playwright`).
- Navegador Chromium para uso com Playwright (`playwright install chromium`).

Instalação básica:

```bash
python -m pip install -r requirements.txt
playwright install chromium
```

## Uso

1) Gerar CPFs válidos

O script `gerar_cpfs.py` pede ao usuário os 6 dígitos centrais do CPF (ex.: `807728`) e gera variações com prefixos `000`–`999`, calculando os dígitos verificadores e salvando cada CPF válido em `cpfvalido.txt`.

Executar:

```bash
python gerar_cpfs.py
```

2) Consultar CPFs (automação)

`consulta_cpf.py` recebe parâmetros pela linha de comando:

- `-f, --file` (obrigatório): arquivo com CPFs (ex.: `cpfvalido.txt`)
- `-n, --name` (obrigatório): primeiro nome a procurar
- `-s, --surname` (obrigatório): sobrenome(s) (pode ser composto)
- `--visual` (opcional): desativa headless e mostra o navegador (por padrão o script roda headless)

Exemplo:

```bash
python consulta_cpf.py -f cpfvalido.txt -n Joao -s Silva
python consulta_cpf.py -f cpfvalido.txt -n Maria -s "da Silva" --visual
```

Comportamento resumido:

- O script abre o site `https://www.jusbrasil.com.br`, realiza busca pelo CPF e verifica o texto da página.
- Se o primeiro nome aparecer na página, o script faz uma varredura por elementos (`div`, `h1`, `h2`, `h3`, `span`) procurando o nome completo informado.
- Resultados são categorizados como `completo` (nome completo encontrado) ou `parcial` (apenas o primeiro nome detectado).
- O script grava resultados parciais em `resultados_busca.txt` e mantém um `checkpoint.json` com o índice atual para retomar execuções interrompidas.
- A cada 5 buscas o contexto do navegador é reiniciado para reduzir risco de bloqueio.

## Arquivos gerados

- `cpfvalido.txt`: lista de CPFs (um por linha) gerada por `gerar_cpfs.py`.
- `resultados_busca.txt`: resultados da busca para o nome informado.
- `checkpoint.json`: checkpoint com índice e resultados parciais para retomar.

## Observações e boas práticas

- Respeite os Termos de Uso e leis locais ao executar buscas automatizadas.
- Executar muitas buscas em sequência pode levar a bloqueios; use `--visual` para testes e monitore o tráfego.
- Ajuste tempos e tratamentos de exceção conforme necessário (o script já realiza reabertura de contexto a cada 5 buscas).

## Troubleshooting rápido

- Se receber erros do Playwright, confirme que instalou os browsers: `playwright install chromium`.
- Se o script não encontra o arquivo, verifique o caminho passado em `-f`.

## Contribuição

- Abra issues para bugs ou melhorias.
- Pull requests são bem-vindos.

---

Desenvolvido por: aburodrigo — use com responsabilidade. 




