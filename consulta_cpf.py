import argparse
import os
import json
import time
import random
from playwright.sync_api import sync_playwright

# ================= FUNÇÃO DO BANNER =================
def exibir_banner(arquivo):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    BRANCO = '\033[97m'
    VERMELHO = '\033[91m'
    VERMELHO_NEGRITO = '\033[1;91m'
    RESET = '\033[0m'

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
{VERMELHO_NEGRITO}    ║                  MODO CDP (MÁXIMA EVASÃO)                        ║{RESET}
{VERMELHO_NEGRITO}    ╠══════════════════════════════════════════════════════════════════╣{RESET}
{VERMELHO}    ║ Status: Conectado ao Chrome Real      {VERMELHO}                           ║{RESET}
{VERMELHO}    ║ Arquivo: {str(arquivo).ljust(51)}     ║{RESET}
{VERMELHO_NEGRITO}    ╚══════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)

# CONFIG DE ARGUMENTOS
parser = argparse.ArgumentParser(description="CPF Discover - Busca de CPF por parâmetros.")
parser.add_argument("-f", "--file", required=True, help="Arquivo .txt com a lista de CPFs")
parser.add_argument("-n", "--name", required=True, help="Primeiro nome do alvo")
parser.add_argument("-s", "--surname", required=True, nargs='+', help="Sobrenome completo do alvo")

args = parser.parse_args()

# ================= TRATAMENTO DOS INPUTS =================
exibir_banner(args.file)

VERMELHO = "\033[91m"
RESET = "\033[0m"

ESTILO = ('===' * 5)

print(f"{VERMELHO}\n {ESTILO} D E S E N V O L V I D O  P O R  A B U R O D R I G O {ESTILO}\n{RESET}")

if not os.path.exists(args.file):
    print(f"❌ ERRO: O arquivo '{args.file}' não foi encontrado.")
    exit()

primeiro_nome = args.name.strip()
sobrenome_completo = " ".join(args.surname).strip()
nome_alvo_completo = f"{primeiro_nome} {sobrenome_completo}".lower()

ARQUIVO_ENTRADA = args.file

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

def simular_scroll_humano(page):
    for _ in range(random.randint(1, 3)):
        page.mouse.wheel(0, random.randint(300, 700))
        time.sleep(random.uniform(0.5, 1.5))
    for _ in range(random.randint(0, 1)):
        page.mouse.wheel(0, -random.randint(200, 400))
        time.sleep(random.uniform(0.5, 1.0))

# ================= EXECUÇÃO PLAYWRIGHT VIA CDP =================

with sync_playwright() as p:
    try:
        # AQUI É ONDE A MÁGICA REAL ACONTECE: 
        # Em vez de criar um navegador robô, ele se conecta ao seu Chrome aberto!
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0] # Pega o contexto já existente
        page = context.new_page()
    except Exception as e:
        print("\n❌ ERRO: Não foi possível conectar ao Chrome.")
        print("Você abriu o Chrome pelo terminal com a porta 9222 conforme as instruções?")
        exit()
    
    def navegar_inicial():
        try:
            page.goto("https://www.google.com.br", wait_until="networkidle", timeout=20000)
            time.sleep(random.uniform(1.0, 2.5))
            page.goto("https://www.jusbrasil.com.br", wait_until="domcontentloaded", timeout=45000)
            time.sleep(random.uniform(2.0, 4.0))
        except: pass

    navegar_inicial()

    idx = indice_inicial
    lote_count = 0

    print(f"🚀 Iniciando varredura via CDP para: {nome_alvo_completo.upper()}...\n")

    while idx < len(cpfs):
        cpf = cpfs[idx]
        print(f"[{idx + 1}/{len(cpfs)}] Analisando CPF: {cpf}")
        
        try:
            search_selector = 'input[name="q"], input[type="search"]'
            searchbox = page.wait_for_selector(search_selector, timeout=15000)
            
            box = searchbox.bounding_box()
            page.mouse.move(box['x'] + box['width'] / 2 + random.randint(-10, 10), 
                            box['y'] + box['height'] / 2 + random.randint(-5, 5), 
                            steps=random.randint(15, 25))
            time.sleep(random.uniform(0.1, 0.4))
            
            page.mouse.down()
            time.sleep(random.uniform(0.05, 0.15))
            page.mouse.up()
            
            page.keyboard.press("Control+A")
            time.sleep(0.1)
            page.keyboard.press("Backspace")
            
            # Digitação humana
            for char in cpf:
                page.keyboard.type(char, delay=random.randint(60, 250))
            
            time.sleep(random.uniform(0.8, 1.5))
            page.keyboard.press("Enter")
            
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(random.uniform(2.5, 4.0)) 
            
            simular_scroll_humano(page)

            body_text = page.inner_text("body").lower()
            
            if primeiro_nome.lower() in body_text:
                found_full_name = False
                elements = page.query_selector_all('div, h1, h2, h3, span')
                
                for el in elements:
                    try:
                        texto_elemento = el.inner_text().lower()
                        if nome_alvo_completo in texto_elemento:
                            found_full_name = True
                            break
                    except: continue

                if found_full_name:
                    print(f"✅ SUCESSO: CPF vinculado ao alvo.")
                    resultados.append((cpf, primeiro_nome, sobrenome_completo, 'completo'))
                else:
                    print(f"⚠️ Primeiro nome ok, sobrenome não encontrado nas Divs.")
                    resultados.append((cpf, primeiro_nome, sobrenome_completo, 'parcial'))

            time.sleep(random.uniform(2.5, 4.5))
            navegar_inicial()
            
            idx += 1
            lote_count += 1
            
            if lote_count >= 5:
                print("🔄 Salvando progresso e esfriando conexão...")
                salvar_checkpoint(idx, resultados)
                salvar_resultados_parcial(resultados, primeiro_nome, sobrenome_completo)
                time.sleep(random.uniform(6, 11))
                navegar_inicial()
                lote_count = 0

        except Exception as e:
            print(f"⏳ Detecção ou Timeout no CPF {cpf}, esfriando a requisição...")
            time.sleep(random.uniform(5, 10))
            navegar_inicial()
            idx += 1

    # Não fechamos o browser aqui, apenas desconectamos, já que o Chrome é seu
    page.close()

# Finalização
salvar_resultados_parcial(resultados, primeiro_nome, sobrenome_completo)
if os.path.exists(checkpoint_file): os.remove(checkpoint_file)

print("\n" + "="*40)
print("✓ Automação concluída com sucesso.")
print("="*40)