import argparse
import os
import json
import time
import re
from playwright.sync_api import sync_playwright

# ================= FUNÇÃO DO BANNER (MANTIDA ORIGINAL) =================
def exibir_banner(modo_headless, arquivo):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    BRANCO = '\033[97m'
    VERMELHO = '\033[91m'
    VERMELHO_NEGRITO = '\033[1;91m'
    RESET = '\033[0m'
    
    status_hl = f"{BRANCO}ATIVADO (Escondido){RESET}" if modo_headless else f"{BRANCO}DESATIVADO (Visual){RESET}"

    banner = f"""
{VERMELHO_NEGRITO}    ╔══════════════════════════════════════════════════════════════════╗{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ║              ██████╗ ██████╗ ███████╗                            ║{RESET}
{VERMELHO_NEGRITO}    ║              ██╔════╝ ██╔══██╗██╔════╝                           ║{RESET}
{VERMELHO_NEGRITO}    ║              ██║      ██████╔╝█████╗                             ║{RESET}
{VERMELHO_NEGRITO}    ║              ██║      ██╔═══╝ ██╔══╝                             ║{RESET}
{VERMELHO_NEGRITO}    ║              ██████╗  ██║     ██║                                ║{RESET}
{VERMELHO_NEGRITO}    ║               ╚═════╝ ╚═╝     ╚═╝                                ║{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ║                      DISCOVER v2.5                               ║{RESET}
{VERMELHO_NEGRITO}    ║               Developed by: aburodrigo                           ║{RESET}
{VERMELHO_NEGRITO}    ╠══════════════════════════════════════════════════════════════════╣{RESET}
{VERMELHO}    ║ Headless: {status_hl.ljust(50)} {RESET}      {VERMELHO}       ║{RESET}
{VERMELHO}    ║ Arquivo: {str(arquivo).ljust(51)}     ║{RESET}
{VERMELHO_NEGRITO}    ╚══════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)

# CONFIG DE ARGUMENTOS
parser = argparse.ArgumentParser(description="CPF Discover - Busca de CPF por parâmetros.")
parser.add_argument("-f", "--file", required=True, help="Arquivo .txt com a lista de CPFs")
parser.add_argument("-n", "--name", required=True, help="Primeiro nome do alvo")
parser.add_argument("-s", "--surname", required=True, nargs='+', help="Sobrenome completo do alvo")
parser.add_argument("--visual", action="store_false", dest="headless", help="Desativa o modo headless")
parser.set_defaults(headless=True)

args = parser.parse_args()

# ================= TRATAMENTO DOS INPUTS =================
exibir_banner(args.headless, args.file)

if not os.path.exists(args.file):
    print(f"❌ ERRO: O arquivo '{args.file}' não foi encontrado.")
    exit()

primeiro_nome = args.name.strip()
sobrenome_completo = " ".join(args.surname).strip()
nome_alvo_completo = f"{primeiro_nome} {sobrenome_completo}".lower()

MODO_ESCONDIDO = args.headless
ARQUIVO_ENTRADA = args.file
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
    cpfs = [cpf.strip() for cpf in f.readlines() if cpf.strip()]

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
    with open("resultados_busca.txt", "w", encoding="utf-8") as f:
        f.write(f"Busca realizada para: {p_nome} {u_nome}\n" + "="*40 + "\n")
        for cpf, nome, sobre, tipo in resultados:
            if tipo == 'completo':
                f.write(f"✅ [NOME ENCONTRADO] CPF: {cpf} - Nome: {nome} {sobre}\n")
            elif tipo == 'parcial':
                f.write(f"⚠️ [PARCIAL]  CPF: {cpf} - Encontrado apenas: {nome}\n")

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
    lote_count = 0

    print(f"🚀 Buscando por: {nome_alvo_completo.upper()}...\n")

    while idx < len(cpfs):
        cpf = cpfs[idx]
        print(f"[{idx + 1}/{len(cpfs)}] Analisando CPF: {cpf}")
        
        try:
            # Busca o CPF
            searchbox = page.wait_for_selector('input[name="q"], input[type="search"]', timeout=10000)
            searchbox.fill(cpf)
            searchbox.press("Enter")
            
            # Espera o carregamento dos resultados
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2.5) 

            # 1. Verificação rápida (Body text)
            body_text = page.inner_text("body").lower()
            
            if primeiro_nome.lower() in body_text:
                print(f"🔎 Primeiro nome detectado. Iniciando varredura de Divs...")
                
                # 2. VALIDAÇÃO DE DIVS (Varre todos os elementos que costumam conter nomes)
                # Buscamos o texto completo dentro de divs, headers e spans
                found_full_name = False
                elements = page.query_selector_all('div, h1, h2, h3, span')
                
                for el in elements:
                    try:
                        texto_elemento = el.inner_text().lower()
                        # Verifica se o nome completo que você inputou aparece dentro de algum desses elementos
                        if nome_alvo_completo in texto_elemento:
                            found_full_name = True
                            break
                    except:
                        continue

                if found_full_name:
                    print(f"✅ SUCESSO: Nome completo encontrado nas Divs: {cpf}")
                    resultados.append((cpf, primeiro_nome, sobrenome_completo, 'completo'))
                else:
                    print(f"⚠️ Nome parcial detectado, mas sobrenome não bateu.")
                    resultados.append((cpf, primeiro_nome, sobrenome_completo, 'parcial'))
            else:
                pass # Nenhum match

            # Reinicia para o próximo CPF
            navegar_inicial()
            idx += 1
            lote_count += 1
            
            # Gerenciamento de Memória/Sessão (Lotes de 5)
            if lote_count >= 5:
                salvar_checkpoint(idx, resultados)
                salvar_resultados_parcial(resultados, primeiro_nome, sobrenome_completo)
                context.close()
                time.sleep(2)
                context = browser.new_context(user_agent=USER_AGENT)
                page = context.new_page()
                navegar_inicial()
                lote_count = 0

        except Exception as e:
            navegar_inicial()
            idx += 1

    browser.close()

# Finalização
salvar_resultados_parcial(resultados, primeiro_nome, sobrenome_completo)
if os.path.exists(checkpoint_file): os.remove(checkpoint_file)

print("\n" + "="*40)
print("✓ Automação finalizada.")
print(f"✓ Resultados salvos em 'resultados_busca.txt'")
print("="*40)