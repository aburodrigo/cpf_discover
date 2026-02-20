#Automação para testar CPFs válidos no JusBrasil

from playwright.sync_api import sync_playwright
import os
import json
import time

def banner_cpf_discover():
    # Códigos de cores ANSI
    VERMELHO = '\033[91m'
    VERMELHO_NEGRITO = '\033[1;91m'
    VERMELHO_CLARO = '\033[91m'
    RESET = '\033[0m'
    
    banner = f"""
{VERMELHO_NEGRITO}    ╔══════════════════════════════════════════════════════════════════╗{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ║                     ██████╗██████╗ ███████╗                     ║{RESET}
{VERMELHO_NEGRITO}    ║                     ██╔════╝██╔══██╗██╔════╝                     ║{RESET}
{VERMELHO_NEGRITO}    ║                     ██║     ██████╔╝█████╗                       ║{RESET}
{VERMELHO_NEGRITO}    ║                     ██║     ██╔═══╝ ██╔══╝                       ║{RESET}
{VERMELHO_NEGRITO}    ║                     ╚██████╗██║     ██║                          ║{RESET}
{VERMELHO_NEGRITO}    ║                      ╚═════╝╚═╝     ╚═╝                          ║{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ║                    ⚡ DISCOVER v1.0 ⚡                           ║{RESET}
{VERMELHO_NEGRITO}    ║              Descoberta e Verificação de CPFs                   ║{RESET}
{VERMELHO_NEGRITO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ╠══════════════════════════════════════════════════════════════════╣{RESET}
{VERMELHO}    ║                                                                  ║{RESET}
{VERMELHO}    ║                 developed by: aburodrigo                         ║{RESET}
{VERMELHO}    ║                                                                  ║{RESET}
{VERMELHO_NEGRITO}    ╚══════════════════════════════════════════════════════════════════╝{RESET}
    """
    print(banner)

# Chamar o banner
banner_cpf_discover()


# Solicitar informações do alvo 
primeiro_nome = input("Digite o primeiro nome que deseja procurar: ").strip()
ultimo_nome = input("Digite o último nome que deseja procurar: ").strip()

print(f"\nProcurando por: {primeiro_nome} {ultimo_nome}")
print("Iniciando testes de CPF...\n")

# Verificar se o arquivo de CPFs válidos existe
if not os.path.exists("cpfvalido.txt"):
    print("Erro: Arquivo 'cpfvalido.txt' não encontrado!")
    exit()

# Ler lista de CPFs
with open("cpfvalido.txt", "r", encoding="utf-8") as f:
    cpfs = [cpf.strip() for cpf in f.readlines() if cpf.strip()]

if not cpfs:
    print("Erro: Nenhum CPF encontrado no arquivo 'cpfvalido.txt'")
    exit()

print(f"Total de CPFs para testar: {len(cpfs)}\n")

# Carregar checkpoint anterior (se existir)
checkpoint_file = "checkpoint.json"
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "r") as f:
        checkpoint = json.load(f)
    indice_inicial = checkpoint.get("indice", 0)
    resultados = checkpoint.get("resultados", [])
    print(f"✓ Retomando do CPF índice {indice_inicial + 1}")
else:
    indice_inicial = 0
    resultados = []

def salvar_checkpoint(indice, resultados):
    """Salva o ponto de parada e resultados até o momento"""
    with open(checkpoint_file, "w") as f:
        json.dump({"indice": indice, "resultados": resultados}, f)

def salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome):
    """Salva apenas os resultados encontrados no arquivo final"""
    # Filtrar apenas os CPFs encontrados
    resultados_encontrados = [r for r in resultados if r[3]]
    
    with open("resultados_busca.txt", "w", encoding="utf-8") as f:
        f.write(f"Alvo procurado: {primeiro_nome} {ultimo_nome}\n")
        f.write(f"Total de CPFs encontrados: {len(resultados_encontrados)}\n")
        f.write("="*60 + "\n\n")
        
        if resultados_encontrados:
            for cpf, nome, sobre, encontrado in resultados_encontrados:
                f.write(f"CPF: {cpf} - Nome encontrado: {nome} {sobre}\n")
        else:
            f.write("Nenhum CPF encontrado para o alvo procurado.\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.jusbrasil.com.br", wait_until="domcontentloaded")

    primeiro_nome_lower = primeiro_nome.lower()
    ultimo_nome_lower = ultimo_nome.lower()
    
    consultas_neste_lote = 0
    max_consultas_por_lote = 5

    idx = indice_inicial
    encontrado = False
    
    while idx < len(cpfs) and not encontrado:
        cpf = cpfs[idx]
        numero_exibicao = idx + 1
        
        print(f"[{numero_exibicao}/{len(cpfs)}] Testando CPF: {cpf}")
        
        try:
            # Preencher o CPF e submeter
            searchbox = page.get_by_role("searchbox", name="Digite um CPF, CNPJ, nome ou")
            searchbox.fill(cpf, timeout=3000)
            searchbox.press("Enter")

            # Aguardar carregamento de resultados (mais rápido)
            page.wait_for_load_state("domcontentloaded", timeout=8000)

            # Verificar se encontrou o alvo usando um método mais rápido
            try:
                page.wait_for_selector("text=" + primeiro_nome, timeout=2000)
                resultado = f"✓ ENCONTRADO - CPF: {cpf} - Nome: {primeiro_nome} {ultimo_nome}"
                print(resultado)
                resultados.append((cpf, primeiro_nome, ultimo_nome, True))
                encontrado = True
            except:
                # Se não encontrou, verificar no texto rapidamente
                text_content = page.text_content("body").lower()
                if primeiro_nome_lower in text_content and ultimo_nome_lower in text_content:
                    resultado = f"✓ ENCONTRADO - CPF: {cpf} - Nome: {primeiro_nome} {ultimo_nome}"
                    print(resultado)
                    resultados.append((cpf, primeiro_nome, ultimo_nome, True))
                    encontrado = True
                else:
                    print(f"✗ Não encontrado - CPF: {cpf}")
                    resultados.append((cpf, primeiro_nome, ultimo_nome, False))

            # Retornar à página inicial de forma mais rápida
            page.goto("https://www.jusbrasil.com.br", wait_until="domcontentloaded")
            
            consultas_neste_lote += 1
            idx += 1
            
            # Se encontrou o alvo, parar imediatamente
            if encontrado:
                print("\n" + "="*60)
                print("✓ ALVO ENCONTRADO! Encerrando busca...")
                print("="*60 + "\n")
                break
            
            # Verificar se atingiu o limite de consultas
            if consultas_neste_lote >= max_consultas_por_lote and idx < len(cpfs):
                # Salvar checkpoint
                salvar_checkpoint(idx, resultados)
                salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome)
                
                # Fechar navegador e fazer pausa
                browser.close()
                
                tempo_pausa = 5  # 5 segundos de pausa
                print("\n" + "="*60)
                print(f"⏸️  PAUSA APÓS 5 CONSULTAS")
                print(f"✓ Processados: {idx} de {len(cpfs)} CPFs")
                print(f"✓ Próximo CPF será: {cpfs[idx]} (índice {idx + 1})")
                print(f"⏳ Aguardando {tempo_pausa} segundos para retomar...")
                print("="*60 + "\n")
                
                time.sleep(tempo_pausa)
                
                # Reiniciar navegador para nova sessão
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto("https://www.jusbrasil.com.br", wait_until="domcontentloaded")
                
                # Resetar contador
                consultas_neste_lote = 0
            
        except Exception as e:
            print(f"✗ Erro ao testar CPF {cpf}: {str(e)}")
            resultados.append((cpf, primeiro_nome, ultimo_nome, False))
            idx += 1
    
    # Fechar navegador
    browser.close()

# Salvar resultados finais
salvar_resultados_parcial(resultados, primeiro_nome, ultimo_nome)

# Remover checkpoint se todos os CPFs foram testados
if os.path.exists(checkpoint_file):
    os.remove(checkpoint_file)

print("\n" + "="*60)
print("✓ Automação concluída!")
print(f"✓ Total processado: {len(resultados)} CPFs")
print(f"✓ Encontrados: {sum(1 for r in resultados if r[3])}")
print(f"✓ Resultados salvos em 'resultados_busca.txt'")
print("="*60)