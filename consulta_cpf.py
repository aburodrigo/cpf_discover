# Automação JusBrasil - Customizável (Headless/Visual)
from playwright.sync_api import sync_playwright
import os
import json
import time
import re

# ================= CONFIGURAÇÕES INICIAIS =================
MODO_ESCONDIDO = True
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
# ==========================================================

def banner_cpf_discover():
    # Códigos de cores ANSI
    BRANCO = '\033[97m'
    VERMELHO = '\033[91m'
    VERMELHO_NEGRITO = '\033[1;91m'
    RESET = '\033[0m'
    status_colorido = f"{BRANCO}ON {RESET}" if MODO_ESCONDIDO else f"{BRANCO}OFF{RESET}"
    
    # Banner ajustado (Largura total: 66 caracteres internos)
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
{VERMELHO_NEGRITO}    ║                      DISCOVER v2.0                               ║{RESET}
{VERMELHO_NEGRITO}    ║             Descoberta e Verificação de CPFs                     ║{RESET}
{VERMELHO_NEGRITO}    ║                    Headless: {status_colorido} {RESET} {VERMELHO_NEGRITO}                               ║{RESET}
{VERMELHO_NEGRITO}    ╠══════════════════════════════════════════════════════════════════╣{RESET}
{VERMELHO}    ║                                                                  ║{RESET}
{VERMELHO}    ║      Desenvolvido por: Rodrigo Carvalho - GitHub: aburodrigo     ║{RESET}
{VERMELHO_NEGRITO}    ╚══════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)

# Chamar o banner
banner_cpf_discover()

primeiro_nome = input("Digite o primeiro nome que deseja procurar: ").strip()
ultimo_nome = input("Digite o último nome que deseja procurar: ").strip()

# Verificação de arquivos
if not os.path.exists("cpfvalido.txt"):
    print("Erro: Arquivo 'cpfvalido.txt' não encontrado!")
    exit()

with open("cpfvalido.txt", "r", encoding="utf-8") as f:
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

def salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome):
    encontrados_completo = [r for r in resultados if r[3] == 'completo']
    encontrados_primeiro = [r for r in resultados if r[3] == 'primeiro']
    with open("resultados_busca.txt", "w", encoding="utf-8") as f:
        f.write(f"Alvo: {primeiro_nome} {ultimo_nome}\n")
        f.write(f"Total (primeiro+último): {len(encontrados_completo)}\n")
        f.write(f"Total (primeiro apenas): {len(encontrados_primeiro)}\n" + "="*40 + "\n")

        if encontrados_completo:
            f.write("Encontrados (primeiro + último):\n")
            for cpf, nome, sobre, tipo in encontrados_completo:
                f.write(f"CPF: {cpf} - Nome: {nome} {sobre}\n")
            f.write("-"*40 + "\n")

        if encontrados_primeiro:
            f.write("Encontrados (primeiro apenas):\n")
            for cpf, nome, sobre, tipo in encontrados_primeiro:
                f.write(f"CPF: {cpf} - Nome: {nome} {sobre}\n")
            f.write("-"*40 + "\n")

with sync_playwright() as p:
    # O parâmetro headless agora é dinâmico
    browser = p.chromium.launch(headless=MODO_ESCONDIDO)
    
    # Contexto persistente com disfarce de bot
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={'width': 1366, 'height': 768}
    )
    
    page = context.new_page()
    
    def navegar_inicial():
        try:
            page.goto("https://www.jusbrasil.com.br", wait_until="domcontentloaded", timeout=30000)
        except:
            pass

    navegar_inicial()

    primeiro_nome_lower = primeiro_nome.lower()
    ultimo_nome_lower = ultimo_nome.lower()
    consultas_neste_lote = 0
    max_consultas_por_lote = 5
    idx = indice_inicial
    encontrado = False
    
    while idx < len(cpfs) and not encontrado:
        cpf = cpfs[idx]
        print(f"[{idx + 1}/{len(cpfs)}] Testando CPF: {cpf}")
        
        try:
            # Seleção robusta do campo de busca
            searchbox = page.wait_for_selector('input[name="q"], input[type="search"]', timeout=10000)
            searchbox.fill("") 
            searchbox.fill(cpf)
            searchbox.press("Enter")

            # Espera carregar a página de resultados
            page.wait_for_load_state("networkidle", timeout=10000)

            try:
                # Busca rápida no conteúdo textual da página (correspondência por palavra)
                body_text = page.inner_text("body").lower()
                # procurar correspondências usando regex com limites de palavra para maior precisão
                found_first = bool(re.search(r"\b" + re.escape(primeiro_nome_lower) + r"\b", body_text))
                found_last = bool(re.search(r"\b" + re.escape(ultimo_nome_lower) + r"\b", body_text))

                if found_first and found_last:
                    print(f"✅ ENCONTRADO (primeiro+último) - CPF: {cpf}")
                    resultados.append((cpf, primeiro_nome, ultimo_nome, 'completo'))
                    encontrado = True
                elif found_first:
                    print(f"ℹ️ Encontrado (primeiro apenas) - CPF: {cpf}")
                    resultados.append((cpf, primeiro_nome, ultimo_nome, 'primeiro'))
                else:
                    print(f"❌ Não encontrado")
                    resultados.append((cpf, primeiro_nome, ultimo_nome, 'none'))
            except:
                resultados.append((cpf, primeiro_nome, ultimo_nome, False))

            # Retorno à home
            navegar_inicial()
            
            consultas_neste_lote += 1
            idx += 1
            
            if encontrado: break
            
            # Gerenciamento de lotes para evitar bloqueios por IP
            if consultas_neste_lote >= max_consultas_por_lote and idx < len(cpfs):
                salvar_checkpoint(idx, resultados)
                salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome)
                
                context.close() 
                print(f"Pausando consulta para bypassar bloqueios... Reiniciando navegador.")
                time.sleep(5)
                
                context = browser.new_context(user_agent=USER_AGENT, viewport={'width': 1366, 'height': 768})
                page = context.new_page()
                navegar_inicial()
                consultas_neste_lote = 0
            
        except Exception as e:
            print(f"⚠️ Erro ao processar. Tentando recuperar...")
            navegar_inicial()
            idx += 1

    browser.close()

# Finalização
salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome)
if os.path.exists(checkpoint_file): os.remove(checkpoint_file)

print("\n" + "="*40)
print("✓ Automação finalizada.")
print(f"✓ Verifique o arquivo 'resultados_busca.txt'")
print("="*40)