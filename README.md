# Descobre CPF - Discovery v1.0

Projeto de automação para descobrir CPFs (Cadastro de Pessoas Físicas) associados a um nome específico através de buscas automatizadas no JusBrasil.

## 📋 Descrição

O projeto consiste em dois scripts principais que trabalham em conjunto:

1. **gerar_cpfs.py** - Gera uma lista de 1.000 CPFs válidos baseado em seis dígitos centrais fornecidos
2. **consulta_cpf.py** - Automatiza buscas de CPFs no JusBrasil com sistema de checkpoint e retomada

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
- Utiliza Playwright para automação de navegador
- Conecta ao portal de buscas JusBrasil (https://www.jusbrasil.com.br)
- Para cada CPF:
  - Preenche o campo de busca com o CPF
  - Submete a pesquisa
  - Analisa o conteúdo da página procurando pelo nome (case-insensitive)
  - Registra como encontrado se ambos primeiro nome e último nome estiverem presentes
  - Retorna à página inicial para próxima busca
- **Sistema de Pausa Inteligente:**
  - Realiza 5 consultas consecutivas
  - Pausa 5 segundos entre lotes para evitar bloqueios
  - Reinicia o navegador a cada lote
- **Sistema de Checkpoint:**
  - Salva progresso em `checkpoint.json`
  - Permite retomar onde parou se interrompido
  - Para a busca automaticamente ao encontrar um CPF associado
- Registra apenas os CPFs encontrados em `resultados_busca.txt`

## ✨ Novas Features

### Retomada Inteligente (Checkpoint)
Se você interromper a busca (Ctrl+C), o progresso é salvo automaticamente. Quando começar a executar o script novamente, ele:
- Detecta o arquivo `checkpoint.json`
- Retoma do CPF onde parou
- Mantém todos os resultados anteriores

### Pausa Automática Entre Consultas
Para evitar bloqueios pelo portal:
- A cada 5 CPFs testados, o script pausa por 5 segundos
- O navegador é reiniciado a cada pausa
- Mostra mensagem informando progresso e próximo CPF

### Parada Imediata ao Encontrar
Quando um CPF associado ao alvo é encontrado:
- A busca para imediatamente
- Evita processar CPFs desnecessários
- Mostra mensagem de sucesso destacada

### Banner Personalizado
O script exibe um banner ASCII decorativo com informações da versão (Discovery v1.0) ao iniciar

## ⚠️ Notas Importantes

- **Termos de Serviço**: Certifique-se de estar em conformidade com os termos do portal utilizado
- **Tempo de Execução**: O script pode levar vários minutos, dependendo da quantidade de CPFs e se encontra o alvo
- **Conexão de Internet**: Requer conexão ativa para acessar o JusBrasil
- **Detectabilidade**: Pode gerar tráfego anômalo ou ser bloqueado por anti-bots
- **Sistema de Pausa**: As pausas automáticas ajudam a evitar bloqueios, mas podem ser ajustadas conforme necessário

## 🔧 Requisitos de Execução

```bash
pip install -r requirements.txt

# Instalar navegador Chromium (se ainda não instalado)
playwright install chromium
```

## 📝 Licença

Este projeto é fornecido como está. Use por sua conta e risco.
