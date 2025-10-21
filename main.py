from xml_parser import XMLParser
from scraper import ProductScraper
from database import Database

def main():
    print("🚀 INICIANDO PLATAFORMA DE ANÁLISE DE CUPONS FISCAIS")
    print("=" * 50)
    
    # 1. Parse XML e carregar no banco
    print("\n📂 ETAPA 1: PROCESSANDO ARQUIVOS XML...")
    parser = XMLParser()
    notas, itens = parser.parse_xml_folder('data/Arquivos-XML-SAT')
    
    print(f"✅ {len(notas)} notas fiscais processadas")
    print(f"✅ {len(itens)} itens extraídos")
    
    # 2. Salvar no banco
    print("\n💾 ETAPA 2: SALVANDO NO BANCO DE DADOS...")
    parser.save_to_database(notas, itens)
    
    # 3. Estatísticas iniciais
    db = Database()
    stats = db.get_stats()
    print(f"📊 ESTATÍSTICAS DO BANCO:")
    print(f"   • Notas fiscais: {stats['total_notas']}")
    print(f"   • Itens: {stats['total_itens']}")
    print(f"   • GTINs únicos: {stats['total_gtins']}")
    print(f"   • Itens enriquecidos: {stats['itens_enriquecidos']}")
    
    # 4. Enriquecer dados (apenas se houver GTINs para enriquecer)
    print("\n🔍 ETAPA 3: ENRIQUECENDO DADOS DOS PRODUTOS...")
    if stats['total_gtins'] > 0:
        scraper = ProductScraper()
        try:
            # Usar o método inteligente que criamos
            scraper.enrich_products_smart(limit=5)
        except Exception as e:
            print(f"⚠️  Aviso no enriquecimento: {e}")
        finally:
            scraper.close()
    else:
        print("ℹ️  Nenhum GTIN encontrado para enriquecimento")
    
    # 5. Estatísticas finais
    print("\n📈 ETAPA 4: RELATÓRIO FINAL")
    final_stats = db.get_stats()
    print("=== RESUMO DO PROCESSAMENTO ===")
    print(f"📄 Notas fiscais processadas: {final_stats['total_notas']}")
    print(f"📦 Itens totais: {final_stats['total_itens']}")
    print(f"🏷️  GTINs únicos: {final_stats['total_gtins']}")
    print(f"✨ Itens enriquecidos: {final_stats['itens_enriquecidos']}")
    
    # 6. Exportar para Excel
    print("\n📊 ETAPA 5: EXPORTANDO PARA EXCEL...")
    try:
        parser.export_to_excel(notas, itens, 'data/processed/relatorio_cfe.xlsx')
        print("✅ Arquivo Excel exportado: data/processed/relatorio_cfe.xlsx")
    except Exception as e:
        print(f"⚠️  Erro ao exportar Excel: {e}")
    
    print("\n🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print("=" * 50)

if __name__ == "__main__":
    # Executar processamento completo
    main()