#Automação para testar CPFs válidos no JusBrasil

from playwright.sync_api import sync_playwright
import time
import os

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

# Armazenar resultados
resultados = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.jusbrasil.com.br")
    page.wait_for_load_state("networkidle")

    for idx, cpf in enumerate(cpfs, 1):
        print(f"[{idx}/{len(cpfs)}] Testando CPF: {cpf}")
        
        try:
            # Garantir que estamos na página inicial e que o campo de busca está disponível
            page.wait_for_load_state("networkidle")
            searchbox = page.get_by_role("searchbox", name="Digite um CPF, CNPJ, nome ou")
            searchbox.wait_for(timeout=5000)

            # Preencher o CPF e submeter
            searchbox.fill("")
            searchbox.fill(cpf)
            searchbox.press("Enter")

            # Aguardar navegação ou carregamento de resultados
            page.wait_for_load_state("networkidle")
            time.sleep(1)

            # Obter texto da página para verificar se contém os nomes
            content = page.content().lower()
            nome_procurado = f"{primeiro_nome} {ultimo_nome}".lower()

            # Verificar se encontrou o alvo
            if primeiro_nome.lower() in content and ultimo_nome.lower() in content:
                resultado = f"✓ ENCONTRADO - CPF: {cpf} - Nome: {primeiro_nome} {ultimo_nome}"
                print(resultado)
                resultados.append((cpf, primeiro_nome, ultimo_nome, True))
            else:
                print(f"✗ Não encontrado - CPF: {cpf}")
                resultados.append((cpf, primeiro_nome, ultimo_nome, False))

            # Após cada busca, garantir que retornamos à página inicial para a próxima iteração
            try:
                page.goto("https://www.jusbrasil.com.br")
                page.wait_for_load_state("networkidle")
                time.sleep(0.5)
            except Exception:
                # Se não conseguir navegar, tentar recarregar
                try:
                    page.reload()
                    page.wait_for_load_state("networkidle")
                    time.sleep(0.5)
                except Exception:
                    pass
            
        except Exception as e:
            print(f"✗ Erro ao testar CPF {cpf}: {str(e)}")
            resultados.append((cpf, primeiro_nome, ultimo_nome, False))
    
    # Fechar navegador
    browser.close()

# Salvar resultados em arquivo
with open("resultados_busca.txt", "w", encoding="utf-8") as f:
    f.write(f"Alvo procurado: {primeiro_nome} {ultimo_nome}\n")
    f.write(f"Total de CPFs testados: {len(cpfs)}\n")
    f.write(f"CPFs encontrados: {sum(1 for r in resultados if r[3])}\n")
    f.write("="*60 + "\n\n")
    
    for cpf, nome, sobre, encontrado in resultados:
        status = "ENCONTRADO" if encontrado else "NÃO ENCONTRADO"
        f.write(f"CPF: {cpf} - Status: {status}\n")

print("\n" + "="*60)
print("Automação concluída!")
print(f"Resultados salvos em 'resultados_busca.txt'")
print("="*60)