import re
import sqlite3
from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('cupons_fiscais.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/top_products')
def top_products():
    try:
        conn = get_db_connection()
        query = '''
            SELECT descricao as produto, SUM(valor_total) as total_vendido
            FROM itens 
            WHERE descricao IS NOT NULL
            GROUP BY descricao 
            ORDER BY total_vendido DESC 
            LIMIT 5
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ ERRO em top_products: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily_revenue')
def daily_revenue():
    try:
        conn = get_db_connection()
        query = '''
            SELECT data_emissao as data, SUM(valor_total) as faturamento
            FROM cupons 
            WHERE data_emissao IS NOT NULL
            GROUP BY data_emissao
            ORDER BY data_emissao
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ ERRO em daily_revenue: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/discount_analysis')
def discount_analysis():
    try:
        conn = get_db_connection()
        query = '''
            SELECT (quantidade * valor_unitario) as valor_bruto, 
                   ((quantidade * valor_unitario) - valor_total) as desconto
            FROM itens
            WHERE quantidade > 0 AND valor_unitario > 0
            LIMIT 100
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ ERRO em discount_analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top_products_quantity')
def top_products_quantity():
    try:
        conn = get_db_connection()
        query = '''
            SELECT descricao as produto, SUM(quantidade) as total_quantidade
            FROM itens 
            WHERE descricao IS NOT NULL
            GROUP BY descricao 
            ORDER BY total_quantidade DESC 
            LIMIT 5
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ ERRO em top_products_quantity: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cfop_sales')
def cfop_sales():
    try:
        conn = get_db_connection()
        query = '''
            SELECT cfop, SUM(valor_total) as total_vendido
            FROM itens 
            WHERE cfop IS NOT NULL
            GROUP BY cfop 
            ORDER BY total_vendido DESC 
            LIMIT 5
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ ERRO em cfop_sales: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/avg_product_value')
def avg_product_value():
    try:
        conn = get_db_connection()
        query = '''
            SELECT descricao as produto, AVG(valor_unitario) as valor_medio
            FROM itens 
            WHERE descricao IS NOT NULL AND valor_unitario > 0
            GROUP BY descricao 
            ORDER BY valor_medio DESC 
            LIMIT 5
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"❌ ERRO em avg_product_value: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def natural_language_query():
    try:
        data = request.get_json()
        pergunta = data.get('pergunta', '').lower()
        
        print(f"🔍 PERGUNTA RECEBIDA: {pergunta}")
        
        conn = get_db_connection()
        
        if 'valor total vendido pela empresa' in pergunta:
            empresa = pergunta.split('empresa')[-1].strip()
            print(f"🔍 BUSCANDO EMPRESA: '{empresa}'")
            
            query = '''
                SELECT SUM(valor_total) as valor_total 
                FROM cupons 
                WHERE UPPER(emitente_razao_social) LIKE UPPER(?)
            '''
            result = conn.execute(query, (f'%{empresa}%',)).fetchone()
            print(f"🔍 RESULTADO EMPRESA: {result[0] if result else 'Nenhum'}")
            
            response = {'resultado': f'Valor total: R$ {result[0]:.2f}' if result[0] else 'Nenhum resultado encontrado'}
        
        elif 'quais empresas compraram o produto' in pergunta:
            produto = pergunta.split('produto')[-1].strip()
            print(f"🔍 BUSCANDO PRODUTO: '{produto}'")
            
            # BUSCA CASE-INSENSITIVE
            query = '''
                SELECT DISTINCT c.emitente_razao_social as empresa
                FROM cupons c
                JOIN itens i ON c.chave_acesso = i.chave_acesso
                WHERE UPPER(i.descricao) LIKE UPPER(?)
            '''
            result = conn.execute(query, (f'%{produto}%',)).fetchall()
            empresas = [row[0] for row in result]
            print(f"🔍 EMPRESAS ENCONTRADAS: {empresas}")
            
            response = {'empresas': empresas if empresas else ['Nenhuma empresa encontrada']}
        
        else:
            response = {'erro': 'Pergunta não reconhecida'}
        
        conn.close()
        return jsonify(response)
    except Exception as e:
        print(f"❌ ERRO em query: {e}")
        return jsonify({'error': str(e)}), 500

# Rota de debug para verificar a estrutura do banco
@app.route('/api/debug')
def debug():
    try:
        conn = get_db_connection()
        
        # Ver tabelas
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        
        # Ver colunas das tabelas
        cupons_columns = conn.execute("PRAGMA table_info(cupons)").fetchall()
        itens_columns = conn.execute("PRAGMA table_info(itens)").fetchall()
        
        # Ver alguns dados
        cupons_sample = conn.execute("SELECT * FROM cupons LIMIT 3").fetchall()
        itens_sample = conn.execute("SELECT * FROM itens LIMIT 3").fetchall()
        
        conn.close()
        
        return jsonify({
            'tables': [table[0] for table in tables],
            'cupons_columns': [col[1] for col in cupons_columns],
            'itens_columns': [col[1] for col in itens_columns],
            'cupons_sample': [dict(row) for row in cupons_sample],
            'itens_sample': [dict(row) for row in itens_sample]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)