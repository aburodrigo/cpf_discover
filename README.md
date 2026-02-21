# CPF Discover - Discovery v2.0

Projeto de automação para descobrir CPFs (Cadastro de Pessoas Físicas) associados a um nome específico através de buscas automatizadas no JusBrasil.

## 📋 Descrição

O projeto consiste em dois scripts principais que trabalham em conjunto:

1. **gerar_cpfs.py** - Gera uma lista de 1.000 CPFs válidos baseado em seis dígitos centrais fornecidos
2. **consulta_cpf.py** - Automatiza buscas de CPFs no JusBrasil com sistema de checkpoint, retomada e modo headless customizável

## 🛠️ Estrutura do Projeto

```
descobre_cpf/
├── gerar_cpfs.py          # Script para gerar CPFs válidos
├── consulta_cpf.py        # Script para consultar CPFs
├── requirements.txt       # Dependências do projeto
├── cpfvalido.txt          # Arquivo com lista de CPFs gerados (criado ao executar)
├── resultados_busca.txt   # Arquivo com resultados das buscas (criado ao executar)
├── checkpoint.json        # Arquivo de checkpoint para retomada (criado durante execução)
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

**Funcionamento:**
- Testa todos os CPFs do arquivo `cpfvalido.txt` buscando pelo nome no JusBrasil
- Após encontrar um CPF associado ao nome, **para a busca automaticamente**
- Realiza até 5 consultas consecutivas, depois faz uma pausa de 5 segundos
- Se interrompido, mantém um checkpoint (arquivo `checkpoint.json`) e pode ser retomado de onde parou
- Registra apenas os CPFs encontrados em `resultados_busca.txt`
- Customizável: altere `MODO_ESCONDIDO` para `True` ou `False` conforme preferir

## 📁 Arquivos Gerados

### cpfvalido.txt
Contém uma lista de CPFs válidos, um por linha. Formato:
```
12345678901
12345678902
...
```

### resultados_busca.txt
Contém apenas os CPFs encontrados associados à pessoa procurada:
```
Alvo procurado: [Nome] [Sobrenome]
Total de CPFs encontrados: X
============================================================

CPF: 12345678901 - Nome encontrado: [Nome] [Sobrenome]
CPF: 12345678902 - Nome encontrado: [Nome] [Sobrenome]
...
```

### checkpoint.json
Arquivo temporário criado durante a execução que armazena:
- O índice do último CPF testado
- Lista de resultados parciais até o momento

Permite retomar a busca do ponto onde foi interrompida.

## ⚙️ Funcionamento Técnico

### Geração de CPFs (gerar_cpfs.py)
- Valida a entrada do usuário (6 dígitos)
- Gera 1.000 variações com diferentes prefixos (000-999)
- Calcula os 2 dígitos verificadores usando o algoritmo oficial do CPF
- Salva todos os CPFs em arquivo

### Consulta de CPFs (consulta_cpf.py)
- Utiliza Playwright para automação de navegador com **modo headless customizável**
- Conecta ao portal de buscas JusBrasil (https://www.jusbrasil.com.br)
- **Variável MODO_ESCONDIDO**: Altere de `False` para `True` no início do script para ativar modo headless
- Para cada CPF:
  - Preenche o campo de busca com o CPF
  - Submete a pesquisa pressionando Enter
  - Analisa o conteúdo da página procurando pelo nome (case-insensitive)
  - Registra como encontrado se ambos primeiro nome e último nome estiverem presentes
  - Retorna à página inicial para próxima busca
- **Sistema de Pausa Inteligente:**
  - Realiza 5 consultas consecutivas
  - Pausa 5 segundos entre lotes para evitar bloqueios
  - Reinicia o navegador e contexto a cada lote com novo user-agent
- **Sistema de Checkpoint:**
  - Salva progresso em `checkpoint.json`
  - Permite retomar onde parou se interrompido
  - Para a busca automaticamente ao encontrar um CPF associado
- Registra apenas os CPFs encontrados em `resultados_busca.txt`

## ✨ Novas Features v2.0

### Modo Headless Customizável
A variável `MODO_ESCONDIDO` permite alternar entre:
- **False**: Modo visual (exibe o navegador enquanto executa) - mais lento mas útil para debug
- **True**: Modo headless (navegador invisível) - mais rápido e consome menos recursos

Para alternar, edite a linha 8 do script:
```python
MODO_ESCONDIDO = False  # Mude para True para ativar headless
```

### Banner Personalizado v2.0
O script exibe um banner ASCII decorativo que mostra:
- Status do modo headless (ON/OFF)
- Versão Discovery v2.0
- Nome do desenvolvedor e GitHub

### User-Agent Customizado
Incluí um User-Agent realista para evitar detecção como bot:
```python
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
```

### Contexto Persistente com Disfarce
Cada nova sessão (após pausa) cria um novo contexto com:
- Janela padronizada (1366x768)
- User-Agent rotativo
- Cookies e histórico limpos entre contextos

## ⚠️ Notas Importantes

- **Configuração Headless**: Antes de executar, decida se quer modo visual ou headless alterando `MODO_ESCONDIDO` (linhas 8-9)
- **Termos de Serviço**: Certifique-se de estar em conformidade com os termos do portal utilizado
- **Tempo de Execução**: O script pode levar vários minutos, dependendo da quantidade de CPFs e se encontra o alvo
- **Conexão de Internet**: Requer conexão ativa para acessar o JusBrasil
- **Detectabilidade**: A pausa automática e os disfarces ajudam a evitar bloqueios, mas o portal pode ainda detectar atividade anômala
- **Modo Headless vs Visual**: 
  - Headless=True: mais rápido, menos recursos, recomendado para lotes grandes
  - Headless=False: mais lento, útil para debugging e ver o que está acontecendo

## 🔧 Requisitos de Execução

```bash
pip install -r requirements.txt

# Instalar navegador Chromium (se ainda não instalado)
playwright install chromium
```

## 📝 Licença

Este projeto é fornecido como está. Use por sua conta e risco.
