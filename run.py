#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import webbrowser

def criar_requirements():
    """Criar arquivo requirements.txt com as libs usadas"""
    print("=== CRIANDO REQUIREMENTS.TXT ===")
    
    libs_essenciais = {
        'flask': 'Framework web',
        'pandas': 'Analise de dados', 
        'selenium': 'Web scraping',
        'lxml': 'Parsing XML',
        'requests': 'Requisicoes HTTP',
        'beautifulsoup4': 'Parsing HTML'
    }
    
    requirements_content = []
    
    for lib, desc in libs_essenciais.items():
        try:
            # Tenta ver a versão instalada
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', lib], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Extrai a versão da saída
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':')[1].strip()
                        requirements_content.append(f"{lib}=={version}")
                        print(f"[OK] {lib}=={version} - {desc}")
                        break
            else:
                requirements_content.append(f"{lib}>=2.0.0")
                print(f"[AVISO] {lib} nao encontrado, usando versao generica")
                
        except Exception as e:
            print(f"[ERRO] Ao verificar {lib}: {e}")
    
    # Escreve no arquivo
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write('# Requirements gerado automaticamente pelo run.py\n')
        f.write('# Libs essenciais para o projeto de Cupons Fiscais\n\n')
        f.write('\n'.join(requirements_content))
    
    print(f"[OK] requirements.txt criado com {len(requirements_content)} libs")

def verificar_dependencias():
    """Verificar e instalar dependências necessárias"""
    print("=== VERIFICANDO DEPENDENCIAS ===")
    
    # Primeiro cria o requirements.txt
    criar_requirements()
    
    # Verifica se requirements.txt existe
    if not os.path.exists('requirements.txt'):
        print("[ERRO] requirements.txt nao foi criado!")
        return False
    
    # Instala dependências do requirements.txt
    try:
        print("Instalando dependencias do requirements.txt...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("[OK] Dependencias instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("[ERRO] Falha ao instalar dependencias")
        return False

def executar_etl():
    """Executar o script de ETL (main.py)"""
    print("\n" + "="*50)
    print("EXECUTANDO ETL (main.py)")
    print("="*50)
    
    if not os.path.exists('main.py'):
        print("[ERRO] main.py nao encontrado! Pulando etapa ETL...")
        return False
    
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        resultado = subprocess.run([sys.executable, 'main.py'], 
                                capture_output=True, 
                                text=True,
                                encoding='utf-8',
                                env=env)
        
        if resultado.returncode == 0:
            print("[OK] ETL executado com sucesso!")
            if resultado.stdout:
                print("Saida:", resultado.stdout)
            return True
        else:
            print("[ERRO] Erro no ETL:")
            if resultado.stderr:
                print(resultado.stderr)
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao executar ETL: {e}")
        return False

def executar_scraping():
    """Executar o script de scraping (scrapper.py)"""
    print("\n" + "="*50)
    print("EXECUTANDO WEB SCRAPING (scrapper.py)")
    print("="*50)
    
    nomes_scrapper = ['scrapper.py', 'scraper.py']
    scrapper_encontrado = None
    
    for nome in nomes_scrapper:
        if os.path.exists(nome):
            scrapper_encontrado = nome
            break
    
    if not scrapper_encontrado:
        print("[AVISO] scrapper.py nao encontrado! Pulando etapa scraping...")
        return False
    
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        resultado = subprocess.run([sys.executable, scrapper_encontrado], 
                                capture_output=True, 
                                text=True,
                                encoding='utf-8',
                                env=env)
        
        if resultado.returncode == 0:
            print("[OK] Web scraping executado com sucesso!")
            if resultado.stdout:
                print("Saida:", resultado.stdout)
            return True
        else:
            print("[ERRO] Erro no scraping:")
            if resultado.stderr:
                print(resultado.stderr)
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao executar scraping: {e}")
        return False

def executar_aplicacao():
    """Executar a aplicação Flask (app.py)"""
    print("\n" + "="*50)
    print("INICIANDO APLICACAO FLASK (app.py)")
    print("="*50)
    
    if not os.path.exists('app.py'):
        print("[ERRO] app.py nao encontrado!")
        return False
    
    if not os.path.exists('cupons_fiscais.db'):
        print("[AVISO] Banco de dados nao encontrado! A aplicacao pode nao funcionar corretamente.")
    
    print("[OK] Ambiente verificado!")
    print("URL: http://localhost:5000")
    print("Dashboard disponivel em 3 segundos...")
    print("Para parar: Ctrl+C")
    print("-" * 50)
    
    def abrir_navegador():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:5000')
        except:
            print("[AVISO] Nao foi possivel abrir o navegador automaticamente")
    
    import threading
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        subprocess.run([sys.executable, 'app.py'], env=env)
    except KeyboardInterrupt:
        print("\n[PARADO] Aplicacao encerrada pelo usuario")
    except Exception as e:
        print(f"[ERRO] Erro na aplicacao: {e}")
        return False
    
    return True

def main():
    """Função principal que orquestra toda a execução"""
    print("INICIANDO PLATAFORMA DE CUPONS FISCAIS")
    print("="*50)
    
    if sys.platform == "win32":
        os.system('chcp 65001 > nul')
    
    # 1. Verificar e instalar dependências
    verificar_dependencias()
    
    # 2. Executar ETL
    etl_sucesso = executar_etl()
    
    # 3. Executar Scraping
    scraping_sucesso = executar_scraping()
    
    # 4. Executar Aplicação
    executar_aplicacao()

if __name__ == "__main__":
    main()