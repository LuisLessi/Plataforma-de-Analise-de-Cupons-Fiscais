import sqlite3
import pandas as pd
import os

class Database:
    def __init__(self, db_path='cupons_fiscais.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas para Cupons Fiscais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de CUPONS FISCAIS (conforme especificado no desafio)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cupons (
                chave_acesso TEXT PRIMARY KEY,
                data_emissao TEXT,
                hora_emissao TEXT,
                valor_total REAL,
                valor_desconto REAL,
                valor_pis REAL,
                valor_cofins REAL,
                emitente_cnpj TEXT,
                emitente_razao_social TEXT,
                forma_pagamento TEXT,
                valor_pagamento REAL,
                destinatario_cpf TEXT,
                destinatario_nome TEXT
            )
        ''')
        
        # Tabela de ITENS dos cupons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave_acesso TEXT,
                numero_item TEXT,
                codigo_produto TEXT,
                codigo_gtin TEXT,
                descricao TEXT,
                ncm TEXT,
                cest TEXT,
                cfop TEXT,
                unidade TEXT,
                quantidade REAL,
                valor_unitario REAL,
                valor_total REAL,
                valor_item_12741 REAL,
                cst_icms TEXT,
                origem_icms TEXT,
                cst_pis TEXT,
                cst_cofins TEXT,
                -- Campos enriquecidos pelo scraping (Parte 1 do desafio)
                descricao_enriquecida TEXT,
                ncm_enriquecido TEXT,
                data_enriquecimento TIMESTAMP,
                FOREIGN KEY (chave_acesso) REFERENCES cupons (chave_acesso)
            )
        ''')
        
        conn.commit()
        
        # Verificar e adicionar colunas faltantes se necessário
        self._check_and_add_columns(conn, cursor)
        
        # Criar índices para performance
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cupons_chave ON cupons(chave_acesso)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_itens_chave ON itens(chave_acesso)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_itens_gtin ON itens(codigo_gtin)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_itens_data ON itens(data_enriquecimento)')
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"⚠️ Aviso ao criar índices: {e}")
        
        conn.close()
        print("✅ Banco de dados inicializado com sucesso!")
    
    def _check_and_add_columns(self, conn, cursor):
        """Verifica e adiciona colunas faltantes para compatibilidade"""
        try:
            cursor.execute("PRAGMA table_info(itens)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Colunas necessárias para o enriquecimento (Parte 1 do desafio)
            required_columns = ['descricao_enriquecida', 'ncm_enriquecido', 'data_enriquecimento']
            
            for column in required_columns:
                if column not in columns:
                    print(f"➕ Adicionando coluna faltante: {column}")
                    if column in ['descricao_enriquecida', 'ncm_enriquecido']:
                        cursor.execute(f"ALTER TABLE itens ADD COLUMN {column} TEXT")
                    elif column == 'data_enriquecimento':
                        cursor.execute(f"ALTER TABLE itens ADD COLUMN {column} TIMESTAMP")
            
            conn.commit()
        except Exception as e:
            print(f"⚠️ Erro ao verificar/adicionar colunas: {e}")
    
    def insert_notas(self, notas_data):
        """Insere cupons fiscais no banco (Parte 1 do desafio - Ingestão)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inseridos = 0
        for nota in notas_data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO cupons 
                    (chave_acesso, data_emissao, hora_emissao, valor_total, valor_desconto, 
                     valor_pis, valor_cofins, emitente_cnpj, emitente_razao_social, 
                     forma_pagamento, valor_pagamento, destinatario_cpf, destinatario_nome)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nota['chave_acesso'], nota['data_emissao'], nota['hora_emissao'],
                    nota['valor_total'], nota['valor_desconto'], nota['valor_pis'],
                    nota['valor_cofins'], nota['emitente_cnpj'], nota['emitente_razao_social'],
                    nota['forma_pagamento'], nota['valor_pagamento'],
                    nota.get('destinatario_cpf'), nota.get('destinatario_nome')
                ))
                if cursor.rowcount > 0:
                    inseridos += 1
            except sqlite3.IntegrityError:
                print(f"⚠️ Cupom {nota['chave_acesso']} já existe no banco.")
            except Exception as e:
                print(f"❌ Erro ao inserir cupom {nota['chave_acesso']}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ {inseridos} cupons inseridos/atualizados no banco.")
    
    def insert_itens(self, itens_data):
        """Insere itens dos cupons no banco (Parte 1 do desafio - Ingestão)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inseridos = 0
        for item in itens_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO itens 
                    (chave_acesso, numero_item, codigo_produto, codigo_gtin, descricao,
                     ncm, cest, cfop, unidade, quantidade, valor_unitario, valor_total,
                     valor_item_12741, cst_icms, origem_icms, cst_pis, cst_cofins)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['chave_acesso'], item['numero_item'], item['codigo_produto'],
                    item['codigo_gtin'], item['descricao'], item['ncm'], item['cest'],
                    item['cfop'], item['unidade'], item['quantidade'], item['valor_unitario'],
                    item['valor_total'], item['valor_item_12741'], item.get('cst_icms'),
                    item.get('origem_icms'), item.get('cst_pis'), item.get('cst_cofins')
                ))
                if cursor.rowcount > 0:
                    inseridos += 1
            except Exception as e:
                print(f"❌ Erro ao inserir item {item['codigo_produto']}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ {inseridos} itens inseridos/atualizados no banco.")
    
    def update_item_info(self, gtin, descricao, ncm):
        """Atualiza informações do produto baseado no GTIN (Parte 1 do desafio - Enriquecimento)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE itens 
                SET descricao_enriquecida = ?, ncm_enriquecido = ?, data_enriquecimento = CURRENT_TIMESTAMP
                WHERE codigo_gtin = ? AND (descricao_enriquecida IS NULL OR ncm_enriquecido IS NULL)
            ''', (descricao, ncm, gtin))
            
            atualizados = cursor.rowcount
            conn.commit()
            
            if atualizados > 0:
                print(f"✅ GTIN {gtin}: {atualizados} itens atualizados")
            else:
                print(f"ℹ️ GTIN {gtin}: Nenhum item atualizado (já possui dados)")
                
        except Exception as e:
            print(f"❌ Erro ao atualizar GTIN {gtin}: {e}")
        finally:
            conn.close()
    
    def get_gtins_para_enriquecer(self, limit=10):
        """Retorna GTINs que ainda não foram enriquecidos (Parte 1 do desafio)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT codigo_gtin 
            FROM itens 
            WHERE codigo_gtin IS NOT NULL 
            AND codigo_gtin != '' 
            AND descricao_enriquecida IS NULL
            LIMIT ?
        ''', (limit,))
        gtins = [row[0] for row in cursor.fetchall()]
        conn.close()
        return gtins
    
    def get_all_cupons(self):
        """Retorna todos os cupons fiscais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cupons ORDER BY data_emissao DESC')
        cupons = cursor.fetchall()
        conn.close()
        return cupons
    
    def get_all_itens(self):
        """Retorna todos os itens"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM itens 
            ORDER BY chave_acesso, CAST(numero_item AS INTEGER)
        ''')
        itens = cursor.fetchall()
        conn.close()
        return itens
    
    def get_stats(self):
        """Estatísticas do banco para relatório"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM cupons')
        total_cupons = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM itens')
        total_itens = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT codigo_gtin) FROM itens WHERE codigo_gtin IS NOT NULL')
        total_gtins = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM itens WHERE descricao_enriquecida IS NOT NULL')
        itens_enriquecidos = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_notas': total_cupons, 
            'total_itens': total_itens,
            'total_gtins': total_gtins,
            'itens_enriquecidos': itens_enriquecidos
        }
    
    def get_dashboard_data(self):
        """Dados para os dashboards (Parte 2 do desafio)"""
        conn = sqlite3.connect(self.db_path)
        
        # Top 5 produtos mais vendidos (Dashboard 1)
        top_produtos = pd.read_sql('''
            SELECT 
                COALESCE(descricao_enriquecida, descricao) as produto,
                SUM(valor_total) as total_vendido
            FROM itens 
            WHERE descricao IS NOT NULL
            GROUP BY produto 
            ORDER BY total_vendido DESC 
            LIMIT 5
        ''', conn)
        
        # Faturamento por dia (Dashboard 2)
        faturamento_dia = pd.read_sql('''
            SELECT 
                data_emissao as data,
                SUM(valor_total) as faturamento
            FROM cupons 
            WHERE data_emissao IS NOT NULL
            GROUP BY data_emissao 
            ORDER BY data_emissao
        ''', conn)
        
        # Análise de descontos (Dashboard 3)
        descontos = pd.read_sql('''
            SELECT 
                (quantidade * valor_unitario) as valor_bruto,
                ((quantidade * valor_unitario) - valor_total) as desconto
            FROM itens
            WHERE quantidade > 0 AND valor_unitario > 0
            LIMIT 100
        ''', conn)
        
        conn.close()
        
        return {
            'top_produtos': top_produtos,
            'faturamento_dia': faturamento_dia,
            'descontos': descontos
        }
    
    def clear_database(self):
        """Limpa todas as tabelas (útil para testes)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM itens')
        cursor.execute('DELETE FROM cupons')
        cursor.execute('UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = "itens"')
        conn.commit()
        conn.close()
        print("🗑️ Banco de dados limpo!")

# Teste rápido do banco
if __name__ == "__main__":
    db = Database()
    stats = db.get_stats()
    print("=== ESTATÍSTICAS DO BANCO ===")
    for key, value in stats.items():
        print(f"{key}: {value}")