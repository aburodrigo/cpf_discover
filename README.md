# CPF Discover — Discovery v2.x

Automação para gerar listas de CPFs válidos e buscar associações de nomes via buscas no JusBrasil.

## 📋 Descrição

O repositório contém dois scripts principais:

- `gerar_cpfs.py` — Gera uma lista de CPFs válidos (arquivo `cpfvalido.txt`).
- `consulta_cpf.py` — Usa Playwright para automatizar buscas por CPF e verificar se um nome (primeiro e último) aparece na página.

Estrutura do projeto:

```
E:\Scripts_Python\cpf_discover\
├── consulta_cpf.py
├── gerar_cpfs.py
├── requirements.txt
├── cpfvalido.txt            # gerado por gerar_cpfs.py
├── resultados_busca.txt     # gerado por consulta_cpf.py
├── checkpoint.json          # gerado por consulta_cpf.py durante execução
└── README.md
```

## Requisitos

- Python 3.7+
- Dependências listadas em `requirements.txt` (por exemplo, `playwright>=1.40.0`).
- Navegador Chromium (instalável via Playwright).

Instalação rápida:

```bash
python -m pip install -r requirements.txt
playwright install chromium
```

## Uso

1) Gerar CPFs válidos

O script `gerar_cpfs.py` solicita ao usuário os 6 dígitos centrais do CPF e gera 1.000 variações (prefixos 000–999), calculando os dígitos verificadores e salvando em `cpfvalido.txt`.

Executar:

```bash
python gerar_cpfs.py
```

2) Consultar CPFs

O script `consulta_cpf.py` aceita argumentos via linha de comando:

- `-f` ou `--file` (obrigatório): caminho para o arquivo de CPFs (ex.: `cpfvalido.txt`)
- `-n` ou `--name` (obrigatório): primeiro nome a procurar
- `-s` ou `--surname` (obrigatório): sobrenome a procurar
- `--visual` (opcional): se passado, desativa o modo headless e abre a janela do navegador (padrão: headless ligado)

Exemplo:

```bash
python consulta_cpf.py -f cpfvalido.txt -n Joao -s Silva --visual
```

Comportamento importante:

- O script lê CPFs do arquivo informado e faz buscas no site https://www.jusbrasil.com.br.
- Para cada CPF a página é pesquisada; se o texto da página contiver o primeiro e o último nome (busca case-insensitive), o CPF é marcado como `completo`.
- Ao encontrar um CPF correspondente, a execução termina (o primeiro resultado completo interrompe a busca).
- Há um sistema de checkpoint (`checkpoint.json`) que salva o índice atual e resultados parciais para retomar a execução.
- O código reinicia o contexto do navegador a cada 5 buscas para reduzir chance de bloqueio.

Arquivos de saída:

- `cpfvalido.txt` — CPFs gerados por `gerar_cpfs.py` (um por linha).
- `resultados_busca.txt` — CPFs encontrados para o nome pesquisado.
- `checkpoint.json` — usado internamente para retomar uma execução interrompida.

## Notas de implementação

- `consulta_cpf.py` usa Playwright (síncrono) e cria um `browser.new_context` com `user_agent` e `viewport` definidos.
- O parâmetro `--visual` no CLI inverte o comportamento padrão (`headless=True` por padrão). Para ver o navegador, passe `--visual`.
- `gerar_cpfs.py` executa interativamente e grava `cpfvalido.txt`.

## Boas práticas e avisos

- Verifique os Termos de Uso do site consultado antes de executar buscas automatizadas.
- Use com responsabilidade e em conformidade com leis de privacidade e proteção de dados.

## Como contribuir

- Abra uma issue para discutir mudanças.
- Envie pull requests para correções e melhorias.




