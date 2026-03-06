# CPF Discover — DISCOVER v2.5

Automação profissional para gerar listas de CPFs válidos e realizar buscas de associações de nomes através de integrações automatizadas com navegadores reais. Utiliza **CDP (Chrome DevTools Protocol)** para máxima evasão de detecção.

## ⚠️ DISCLAIMER LEGAL

**Este projeto é fornecido exclusivamente para fins legais e éticamente responsáveis.** 

O uso desta ferramenta está condicionado ao cumprimento total das leis aplicáveis, incluindo mas não limitado a:
- Leis de proteção de dados e privacidade (Lei Geral de Proteção de Dados - LGPD)
- Termos de Serviço das plataformas utilizadas (JusBrasil, Google, etc.)
- Legislação relacionada a acesso não autorizado de sistemas
- Leis contra fraude e roubo de identidade

**Os desenvolvedores deste projeto NÃO SE RESPONSABILIZAM por:**
- Uso inadequado, ilegal ou não ético desta ferramenta
- Violação de leis, regulamentações ou direitos de terceiros
- Danos causados pelo uso indevido, incluindo processos legais
- Bloqueios, banimentos ou consequências por detecção em plataformas

Ao utilizar este código, você assume total responsabilidade legal pelas suas ações. Use apenas com consentimento explícito e para propósitos legítimos e autorizados.

## Visão geral

Este repositório contém dois scripts principais:

- **`gerar_cpfs.py`**: Gera CPFs válidos a partir de 6 dígitos centrais fornecidos pelo usuário. Calcula os dígitos verificadores de forma correta e salva uma lista de 1000 variações em `cpfvalido.txt`.
- **`consulta_cpf.py`**: Automatiza buscas utilizando Playwright conectado a um Chrome real via CDP. Verifica se um nome específico aparece nos resultados das buscas de CPF no JusBrasil, com detecção de correspondências completas e parciais.

Estrutura do projeto:

```
E:/Scripts_Python/cpf_discover/
├── consulta_cpf.py          # Script de consulta via CDP
├── gerar_cpfs.py            # Gerador de CPFs válidos
├── requirements.txt         # Dependências Python
├── README.md                # Este arquivo
├── cpfvalido.txt            # Gerado por gerar_cpfs.py
├── resultados_busca.txt     # Gerado por consulta_cpf.py
├── checkpoint.json          # Checkpoint de execução (automático)
└── __pycache__/             # Cache Python
```

## Requisitos

- **Python 3.7+**
- **Dependências**: Playwright (veja `requirements.txt`)
- **Navegador Chrome/Chromium**: Deve estar instalado e executável
- **Chrome com CDP ativo**: Para `consulta_cpf.py`, requer Chrome aberto com suporte CDP na porta 9222

### Instalação

```bash
# Instalar dependências
python -m pip install -r requirements.txt

# Instalar Chromium (se necessário)
playwright install chromium
```

## Uso

### 1. Gerar CPFs válidos

O script `gerar_cpfs.py` solicita os 6 dígitos centrais de um CPF e gera uma lista de 1000 CPFs válidos (com prefixos de `000` a `999`), calculando corretamente os dois dígitos verificadores.

**Executar:**

```bash
python gerar_cpfs.py
```

**Entrada esperada:**
```
Digite os seis dígitos centrais do CPF (ex: 807728): 807728
```

**Saída:**
- Arquivo `cpfvalido.txt` com 1000 CPFs válidos (um por linha)

### 2. Consultar CPFs (automação via CDP)

**⚠️ PRÉ-REQUISITO IMPORTANTE:**

Antes de executar `consulta_cpf.py`, você deve abrir o Chrome com CDP ativo:

```bash
# No Windows (PowerShell ou CMD)
C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_temp_profile

# No Linux/macOS
pasta_do_chrome/google-chrome --remote-debugging-port=9222
```

Ou, se usar Chromium:
```bash
chromium --remote-debugging-port=9222
```

**Parâmetros de linha de comando:**

- `-f, --file` **(obrigatório)**: Caminho do arquivo com CPFs (ex: `cpfvalido.txt`)
- `-n, --name` **(obrigatório)**: Primeiro nome a procurar
- `-s, --surname` **(obrigatório)**: Sobrenome(s) (pode ser composto)

**Exemplos:**

```bash
python consulta_cpf.py -f cpfvalido.txt -n Joao -s Silva
python consulta_cpf.py -f cpfvalido.txt -n Maria -s "da Silva Oliveira"
python consulta_cpf.py -f cpfvalido.txt -n Pedro -s "dos Santos"
```

### Comportamento da automação

1. **Conecta via CDP**: O script se conecta ao Chrome aberto numa porta específica (9222), sem abrir um navegador adicional.
2. **Simula comportamento humano**: 
   - Movimento natural do mouse com variação aleatória
   - Digitação lenta e realista (60-250ms entre caracteres)
   - Scroll aleatório e variável nas páginas
   - Tempos de espera naturais entre ações
3. **Busca estruturada**:
   - Navega para Google.com.br e JusBrasil.com.br (comportamento de usuário real)
   - Realiza busca pelo CPF
   - Verifica se o primeiro nome aparece no texto da página
   - Se encontrado, procura pelo nome completo em elementos específicos (`div`, `h1`, `h2`, `h3`, `span`)
4. **Categorização de resultados**:
   - ✅ **COMPLETO**: Nome e sobrenome encontrados
   - ⚠️ **PARCIAL**: Apenas o primeiro nome detectado
5. **Sistema de checkpoint e retomada**:
   - Salva progresso a cada 5 CPFs em `checkpoint.json`
   - Permite retomar execução interrompida automaticamente
   - Gera `resultados_busca.txt` com os achados
6. **Proteção contra bloqueios**:
   - A cada 5 buscas, aguarda 6-11 segundos ("esfriando a conexão")
   - Reinicia navegação para reduzir risco de detecção
   - Trata exceções e timeouts gracefully

## Arquivos gerados

- **`cpfvalido.txt`**: Lista de CPFs válidos (1000 linhas), um por linha
- **`resultados_busca.txt`**: Resultados da busca (nomes encontrados com status completo/parcial)
- **`checkpoint.json`**: Backup automático do progresso (índice atual + resultados parciais)

## Recursos técnicos

- **Playwright**: Automação de navegador com suporte a CDP
- **CDP (Chrome DevTools Protocol)**: Conexão direta ao Chrome sem emulação robótica
- **Simulação de comportamento humano**: Delays variáveis, scroll aleatório, movimento de mouse
- **Tratamento robusto de erros**: Timeout handling, retomada de execução

## Observações e boas práticas

- 🔒 **Responsabilidade legal**: Respeite os Termos de Uso do JusBrasil e leis locais
- ⚖️ **Privacidade**: Use apenas para propósitos legítimos e éticos
- 🛡️ **Detecção**: Para testes, monitore o navegador e o tráfego; ajuste timings se necessário
- ⏱️ **Performance**: A automatização é intencionalesta lenta para evitar bloqueios
- ✏️ **Customização**: Todos os delays, seletores e timeouts podem ser ajustados no código

## Troubleshooting

| Erro | Solução |
|------|---------|
| "Não foi possível conectar ao Chrome" | Abra o Chrome com `--remote-debugging-port=9222` |
| "Arquivo não encontrado" | Verifique o caminho do arquivo com `-f` |
| "Erro no Playwright" | Execute `playwright install chromium` |
| "Bloqueio de IP/detecção" | Aumente os delays no código ou aguarde antes de nova execução |
| Execução interrompida | Execute novamente; o `checkpoint.json` retomará de onde parou |

## Desenvolvimento

- Linguagem: Python 3.7+
- Dependências principais: `playwright`
- Estrutura modular com funções bem definidas
- Suporte a checkpoint e retomada automática

---

**Desenvolvido por:** aburodrigo

**Versão:** 2.5 — Modo CDP (Máxima Evasão)

⚠️ **Use com responsabilidade e respeito às leis aplicáveis.** 




