from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random
from database import Database

class ProductScraper:
    def __init__(self):
        self.db = Database()
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Voltar ao headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def analisar_gtins_do_banco(self):
        """Analisa os GTINs reais dos seus XMLs"""
        print("=== ANALISANDO GTINS DOS SEUS XMLs ===")
        
        itens = self.db.get_all_itens()
        gtins_unicos = {}
        
        for item in itens:
            gtin = item[4]  # codigo_gtin
            descricao = item[5]  # descricao
            ncm = item[6]  # ncm
            
            if gtin and gtin != 'None' and gtin != 'SEM GTIN' and len(gtin) >= 8:
                if gtin not in gtins_unicos:
                    gtins_unicos[gtin] = {
                        'descricao': descricao,
                        'ncm': ncm,
                        'quantidade': 1
                    }
                else:
                    gtins_unicos[gtin]['quantidade'] += 1
        
        print(f"Total de GTINs únicos encontrados: {len(gtins_unicos)}")
        
        # Separar GTINs reais vs códigos internos
        gtins_reais = {}
        gtins_internos = {}
        
        for gtin, info in gtins_unicos.items():
            if gtin.startswith(('789', '790')):  # GTINs brasileiros reais
                gtins_reais[gtin] = info
            else:
                gtins_internos[gtin] = info
        
        print(f"✅ GTINs reais (789/790): {len(gtins_reais)}")
        print(f"⚠️  Códigos internos: {len(gtins_internos)}")
        
        # Mostrar top GTINs reais
        gtins_reais_ordenados = sorted(gtins_reais.items(), key=lambda x: x[1]['quantidade'], reverse=True)
        
        print(f"\n=== TOP 10 GTINS REAIS MAIS VENDIDOS ===")
        for i, (gtin, info) in enumerate(gtins_reais_ordenados[:10]):
            print(f"{i+1}. GTIN: {gtin}")
            print(f"   Descrição: {info['descricao']}")
            print(f"   NCM: {info['ncm']}")
            print(f"   Frequência: {info['quantidade']} vendas")
            print()
        
        return gtins_reais, gtins_internos
    
    def get_product_info_manual(self, gtin):
        """Busca manual baseada no GTIN conhecido - ATUALIZADA"""
        # Base expandida com produtos dos seus XMLs
        gtin_database = {
            # SEUS PRODUTOS REAIS (do analysis)
            "7622300861148": ("REFRIGERANTE TANG 25G", "21069010"),
            "7622300861308": ("REFRIGERANTE TANG 25G", "21069010"),
            "7622300861261": ("REFRIGERANTE TANG 25G", "21069010"),
            "7622300861223": ("REFRIGERANTE TANG 25G", "21069010"),
            "7896273100393": ("ENERGÉTICO RED TIGER 2L", "22029900"),
            "7898080640017": ("LEITE LONGA VIDA ITALAC 1L", "04012010"),
            "7896279600538": ("ÓLEO DE SOJA COAMO 900ML", "15079011"),
            "7898954959078": ("COENTRO HIDROPÔNICO", "07108000"),
            "7896045505357": ("CERVEJA HEINEKEN 250ML", "22030000"),
            "7894900011517": ("REFRIGERANTE COCA-COLA 2L", "22021000"),
            "7894900011012": ("REFRIGERANTE COCA-COLA LATA 350ML", "22021000"),
            "7891000305508": ("LEITE CONDENSADO MOÇA 395G", "04029900"),
            "7893000362549": ("SABÃO EM PÓ OMO 1KG", "34012090"),
            "7891156003068": ("LEITE FERMENTADO YAKULT 80G", "04039000"),
            "7891203010308": ("PÃO DE FORMA PANCO COCO 350G", "19059090"),
            "7894000182018": ("BEBIDA DE SOJA ADES MAÇÃ 1L", "22029900"),
            "7896353301184": ("REQUEIJÃO CATUPIRY 200G", "04061090")
        }
        
        if gtin in gtin_database:
            descricao, ncm = gtin_database[gtin]
            print(f"📦 GTIN encontrado na base local: {descricao}")
            return descricao, ncm
        
        return None, None
    
    def get_product_info_brasilapi(self, gtin):
        """Tenta buscar no Brasil API - VERSÃO MELHORADA"""
        if not gtin or gtin == 'None':
            return None, None
        
        # Pular códigos internos (não são GTINs reais)
        if not gtin.startswith(('789', '790')):
            return None, None
        
        try:
            url = f"https://brasilapi.com.br/api/gtins/v1/{gtin}"
            print(f"🌐 Buscando GTIN no Brasil API: {gtin}")
            self.driver.get(url)
            
            time.sleep(2)
            
            # Verificar se a página carregou corretamente (não é página de erro)
            page_source = self.driver.page_source
            
            if "error" in page_source.lower() or "not found" in page_source.lower():
                return None, None
            
            if "description" in page_source:
                import json
                import re
                
                json_match = re.search(r'\{.*\}', page_source)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        descricao = data.get('description', '')
                        ncm = data.get('ncm', '')
                        
                        if descricao and len(descricao) > 5:
                            return descricao, ncm
                    except:
                        pass
            
            return None, None
            
        except Exception as e:
            print(f"❌ Erro no Brasil API para {gtin}: {e}")
            return None, None
    
    def get_product_info(self, gtin):
        """Tenta múltiplas fontes para obter informações do produto"""
        if not gtin or gtin == 'None':
            return None, None
        
        print(f"\n🔍 Buscando informações para GTIN: {gtin}")
        
        # Tentar base local primeiro (mais rápido)
        descricao, ncm = self.get_product_info_manual(gtin)
        if descricao:
            return descricao, ncm
        
        # Para GTINs reais, tentar API
        descricao, ncm = self.get_product_info_brasilapi(gtin)
        if descricao:
            return descricao, ncm
        
        print(f"❌ Nenhuma informação encontrada para GTIN: {gtin}")
        return None, None
    
    def enrich_products_smart(self, limit=10):
        """Enriquece apenas produtos com GTINs reais"""
        gtins_reais, gtins_internos = self.analisar_gtins_do_banco()
        
        print(f"\n🎯 ENRIQUECENDO PRODUTOS (GTINs REAIS)")
        print(f"Total de GTINs reais disponíveis: {len(gtins_reais)}")
        
        # Pegar os GTINs reais mais frequentes
        gtins_para_enriquecer = sorted(gtins_reais.items(), key=lambda x: x[1]['quantidade'], reverse=True)[:limit]
        
        print(f"Processando {len(gtins_para_enriquecer)} GTINs reais...")
        
        for i, (gtin, info) in enumerate(gtins_para_enriquecer):
            print(f"\n--- Produto {i+1}/{len(gtins_para_enriquecer)}: {gtin} ---")
            print(f"Descrição atual: {info['descricao']}")
            
            descricao, ncm = self.get_product_info(gtin)
            
            if descricao:
                print(f"✅ NOVA Descrição: {descricao}")
                print(f"✅ NCM: {ncm}")
                
                # Atualizar no banco
                self.db.update_item_info(gtin, descricao, ncm)
            else:
                print("ℹ️  Mantendo descrição original")
            
            time.sleep(random.uniform(1, 3))
        
        print(f"\n🎉 Enriquecimento inteligente concluído!")
    
    def close(self):
        self.driver.quit()
        print("🔚 Driver fechado.")

# Função de teste ATUALIZADA
def test_scraper():
    print("=== TESTANDO WEB SCRAPER INTELIGENTE ===")
    
    scraper = ProductScraper()
    
    try:
        # Análise completa + enriquecimento inteligente
        scraper.enrich_products_smart(limit=5)
        
    except Exception as e:
        print(f"❌ Erro durante scraping: {e}")
    
    finally:
        scraper.close()

# Execução direta do arquivo
if __name__ == "__main__":
    test_scraper()