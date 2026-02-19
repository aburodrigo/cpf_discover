# Descobre CPF

Projeto de automação para descobrir CPFs (Cadastro de Pessoas Físicas) associados a um nome específico através de buscas automatizadas.

## 📋 Descrição

O projeto consiste em dois scripts principais que trabalham em conjunto:

1. **gerar_cpfs.py** - Gera uma lista de CPFs válidos baseado em uma sequência de dígitos fornecida
2. **consulta_cpf.py** - Automatiza buscas de CPFs em portal de informações públicas

## 🛠️ Estrutura do Projeto

```
descobre_cpf/
├── gerar_cpfs.py          # Script para gerar CPFs válidos
├── consulta_cpf.py        # Script para consultar CPFs
├── cpfvalido.txt          # Arquivo com lista de CPFs gerados (criado ao executar)
├── resultados_busca.txt   # Arquivo com resultados das buscas (criado ao executar)
└── README.md              # Este arquivo
```

## 🚀 Como Usar

### Pré-requisitos

- Python 3.7+
- Playwright: `pip install playwright`
- Navegador Chromium instalado: `playwright install`

### Passo 1: Gerar CPFs Válidos

Execute o script `gerar_cpfs.py`:

```bash
python gerar_cpfs.py
```

O script solicitará que você digite **6 dígitos centrais** do CPF (ex: `807728`).

Ele gerará 1.000 CPFs válidos com essa sequência central, calculando automaticamente os dígitos verificadores corretos. Os CPFs serão salvos em `cpfvalido.txt`.

### Passo 2: Consultar CPFs

Execute o script `consulta_cpf.py`:

```bash
python consulta_cpf.py
```

O script solicitará:
- **Primeiro nome** da pessoa que você deseja procurar
- **Último nome** da pessoa

Ele testará todos os CPFs do arquivo `cpfvalido.txt`, buscando pelo nome em um portal public e registrará quais CPFs estão associados à pessoa procurada.

Os resultados serão salvos em `resultados_busca.txt`.

## 📁 Arquivos Gerados

### cpfvalido.txt
Contém uma lista de CPFs válidos, um por linha. Formato:
```
12345678901
12345678902
...
```

### resultados_busca.txt
Contém os resultados das buscas realizadas:
```
Alvo procurado: [Nome] [Sobrenome]
Total de CPFs testados: 1000
CPFs encontrados: X
============================================================

CPF: 12345678901 - Status: ENCONTRADO
CPF: 12345678902 - Status: NÃO ENCONTRADO
...
```

## ⚙️ Funcionamento Técnico

### Geração de CPFs (gerar_cpfs.py)
- Valida a entrada do usuário (6 dígitos)
- Gera 1.000 variações com diferentes prefixos (000-999)
- Calcula os 2 dígitos verificadores usando o algoritmo oficial do CPF
- Salva todos os CPFs em arquivo

### Consulta de CPFs (consulta_cpf.py)
- Utiliza Playwright para automação de navegador
- Abre portal de buscas (JusBrasil)
- Para cada CPF:
  - Preenche o campo de busca
  - Submete a pesquisa
  - Analisa o conteúdo da página procurando pelo nome
  - Retorna à página inicial para próxima busca
- Registra resultados com status de encontrado/não encontrado

## ⚠️ Notas Importantes

- **Termos de Serviço**: Certifique-se de estar em conformidade com os termos do portal utilizado
- **Tempo de Execução**: O script pode levar vários minutos, dependendo da quantidade de CPFs
- **Conexão de Internet**: Requer conexão ativa para acessar o portal
- **Detectabilidade**: Pode gerar tráfego anômalo ou ser bloqueado por anti-bots

## 🔧 Requisitos de Execução

```bash
pip install playwright

# Instalar navegador Chromium
playwright install chromium
```

## 📝 Licença

Este projeto é fornecido como está. Use por sua conta e risco.
