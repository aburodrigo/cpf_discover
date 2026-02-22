import argparse
import os
import json
import time
import re
from playwright.sync_api import sync_playwright

# ================= FUNÇÃO DO BANNER =================
def exibir_banner(modo_headless, arquivo):
    # Limpa o terminal antes de exibir
    os.system('cls' if os.name == 'nt' else 'clear')
    
    BRANCO = '\033[97m'
    VERMELHO = '\033[91m'
    VERMELHO_NEGRITO = '\033[1;91m'
    RESET = '\033[0m'
    
    status_hl = f"{BRANCO}ATIVADO (Escondido){RESET}" if modo_headless else f"{BRANCO}DESATIVADO (Visual){RESET}"

    banner = f"""
{VERMELHO_NEGRITO}    ╔══════════════════════════════════════════════════════════════════╗{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ║             ██████╗ ██████╗ ███████╗                             ║{RESET}
{VERMELHO_NEGRITO}    ║             ██╔════╝ ██╔══██╗██╔════╝                            ║{RESET}
{VERMELHO_NEGRITO}    ║             ██║      ██████╔╝█████╗                              ║{RESET}
{VERMELHO_NEGRITO}    ║             ██║      ██╔═══╝ ██╔══╝                              ║{RESET}
{VERMELHO_NEGRITO}    ║             ██████╗  ██║     ██║                                 ║{RESET}
{VERMELHO_NEGRITO}    ║              ╚═════╝ ╚═╝     ╚═╝                                 ║{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ║                      DISCOVER v2.5                               ║{RESET}
{VERMELHO_NEGRITO}    ║              Descoberta e Verificação de CPFs                    ║{RESET}
{VERMELHO_NEGRITO}    ╠══════════════════════════════════════════════════════════════════╣{RESET}
{VERMELHO}    ║ Headless: {status_hl.ljust(50)} {RESET}      {VERMELHO}       ║{RESET}
{VERMELHO}    ║ Arquivo: {str(arquivo).ljust(51)}     ║{RESET}
{VERMELHO_NEGRITO}    ╚══════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)

# CONFIG DE ARGUMENTOS 
parser = argparse.ArgumentParser(description="CPF Discover - Busca de CPF por parâmetros.")

# Parâmetros
parser.add_argument("-f", "--file", required=True, help="Arquivo .txt com a lista de CPFs (um por linha)")
parser.add_argument("-n", "--name", required=True, help="Primeiro nome do alvo")
parser.add_argument("-s", "--surname", required=True, help="Último nome (sobrenome) do alvo")

# Parâmetro opcional para o Headless (Padrão é True)
parser.add_argument("--visual", action="store_false", dest="headless", 
                    help="Desativa o modo headless (abre a janela do navegador)")
parser.set_defaults(headless=True)

args = parser.parse_args()

# ================= INÍCIO DO SCRIPT =================

# 1. Exibir o banner imediatamente com os dados coletados
exibir_banner(args.headless, args.file)

# Validação do arquivo
if not os.path.exists(args.file):
    print(f"❌ ERRO: O arquivo '{args.file}' não foi encontrado na pasta.")
    exit()

# Variáveis globais baseadas nos parâmetros
MODO_ESCONDIDO = args.headless
ARQUIVO_ENTRADA = args.file
primeiro_nome = args.name
ultimo_nome = args.surname
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Carregar CPFs
with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
    cpfs = [cpf.strip() for cpf in f.readlines() if cpf.strip()]

# Lógica de Checkpoint
checkpoint_file = "checkpoint.json"
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "r") as f:
        checkpoint = json.load(f)
    indice_inicial = checkpoint.get("indice", 0)
    resultados = checkpoint.get("resultados", [])
else:
    indice_inicial = 0
    resultados = []

def salvar_checkpoint(indice, resultados):
    with open(checkpoint_file, "w") as f:
        json.dump({"indice": indice, "resultados": resultados}, f)

def salvar_resultados_parcial(resultados, p_nome, u_nome):
    encontrados_completo = [r for r in resultados if r[3] == 'completo']
    with open("resultados_busca.txt", "w", encoding="utf-8") as f:
        f.write(f"Busca realizada para: {p_nome} {u_nome}\n" + "="*40 + "\n")
        if encontrados_completo:
            for cpf, nome, sobre, tipo in encontrados_completo:
                f.write(f"CPF: {cpf} - Nome: {nome} {sobre}\n")

# ================= EXECUÇÃO PLAYWRIGHT =================

with sync_playwright() as p:
    browser = p.chromium.launch(headless=MODO_ESCONDIDO)
    context = browser.new_context(user_agent=USER_AGENT, viewport={'width': 1366, 'height': 768})
    page = context.new_page()
    
    def navegar_inicial():
        try:
            page.goto("https://www.jusbrasil.com.br", wait_until="domcontentloaded", timeout=30000)
        except: pass

    navegar_inicial()

    idx = indice_inicial
    encontrado = False
    lote_count = 0

    print(f"🚀 Buscando por: {primeiro_nome} {ultimo_nome}...\n")

    while idx < len(cpfs) and not encontrado:
        cpf = cpfs[idx]
        print(f"[{idx + 1}/{len(cpfs)}] Testando CPF: {cpf}")
        
        try:
            searchbox = page.wait_for_selector('input[name="q"], input[type="search"]', timeout=10000)
            searchbox.fill(cpf)
            searchbox.press("Enter")
            page.wait_for_load_state("networkidle", timeout=10000)

            body_text = page.inner_text("body").lower()
            found_first = bool(re.search(r"\b" + re.escape(primeiro_nome.lower()) + r"\b", body_text))
            found_last = bool(re.search(r"\b" + re.escape(ultimo_nome.lower()) + r"\b", body_text))

            if found_first and found_last:
                print(f"✅ CPF CORRESPONDENTE: {cpf}")
                resultados.append((cpf, primeiro_nome, ultimo_nome, 'completo'))
                encontrado = True
            else:
                resultados.append((cpf, primeiro_nome, ultimo_nome, 'none'))

            navegar_inicial()
            idx += 1
            lote_count += 1
            
            if lote_count >= 5:
                salvar_checkpoint(idx, resultados)
                salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome)
                context.close()
                time.sleep(3)
                context = browser.new_context(user_agent=USER_AGENT)
                page = context.new_page()
                navegar_inicial()
                lote_count = 0

        except Exception:
            navegar_inicial()
            idx += 1

    browser.close()

# Finalização
salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome)
if os.path.exists(checkpoint_file): os.remove(checkpoint_file)

print("\n" + "="*40)
print("✓ Automação finalizada.")
print("="*40)