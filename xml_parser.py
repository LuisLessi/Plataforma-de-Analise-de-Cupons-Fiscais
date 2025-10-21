import xml.etree.ElementTree as ET
import pandas as pd
import os
from database import Database

class XMLParser:
    def __init__(self):
        self.db = Database()
    
    def parse_xml_folder(self, folder_path):
        notas_data = []
        itens_data = []
        
        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                file_path = os.path.join(folder_path, filename)
                nota, itens = self.parse_xml_file(file_path)
                if nota:
                    notas_data.append(nota)
                    itens_data.extend(itens)
        
        return notas_data, itens_data
    
    def convert_date(self, date_str):
        """Converte data de YYYYMMDD para YYYY-MM-DD"""
        if date_str and len(date_str) == 8:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return date_str
    
    def parse_xml_file(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Namespace do CFe
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            
            # Encontrar a tag infCFe
            infCFe = root.find('.//infCFe')
            if infCFe is None:
                print(f"Arquivo {file_path} não contém tag infCFe")
                return None, []
            
            # Extrair dados da nota (estrutura real do CFe SAT)
            ide = infCFe.find('ide')
            emit = infCFe.find('emit')
            total = infCFe.find('total/ICMSTot')
            pgto = infCFe.find('pgto')
            
            nota = {
                'chave_acesso': infCFe.get('Id', '').replace('CFe', ''),
                'numero_caixa': ide.find('numeroCaixa').text if ide.find('numeroCaixa') is not None else None,
                # DATA CORRIGIDA AQUI ↓
                'data_emissao': self.convert_date(ide.find('dEmi').text) if ide.find('dEmi') is not None else None,
                'hora_emissao': ide.find('hEmi').text if ide.find('hEmi') is not None else None,
                'valor_total': float(total.find('vProd').text) if total.find('vProd') is not None else 0.0,
                'valor_desconto': float(total.find('vDesc').text) if total.find('vDesc') is not None else 0.0,
                'valor_pis': float(total.find('vPIS').text) if total.find('vPIS') is not None else 0.0,
                'valor_cofins': float(total.find('vCOFINS').text) if total.find('vCOFINS') is not None else 0.0,
                'emitente_cnpj': emit.find('CNPJ').text if emit.find('CNPJ') is not None else None,
                'emitente_razao_social': emit.find('xNome').text if emit.find('xNome') is not None else None,
                'forma_pagamento': pgto.find('MP/cMP').text if pgto.find('MP/cMP') is not None else None,
                'valor_pagamento': float(pgto.find('MP/vMP').text) if pgto.find('MP/vMP') is not None else 0.0
            }
            
            # Extrair dados do destinatário (se existir)
            dest = infCFe.find('dest')
            if dest is not None:
                nota['destinatario_cpf'] = dest.find('CPF').text if dest.find('CPF') is not None else None
                nota['destinatario_nome'] = dest.find('xNome').text if dest.find('xNome') is not None else None
            else:
                nota['destinatario_cpf'] = None
                nota['destinatario_nome'] = None
            
            # Extrair itens
            itens = []
            for det in infCFe.findall('det'):
                prod = det.find('prod')
                imposto = det.find('imposto')
                
                # Informações do produto
                item = {
                    'chave_acesso': nota['chave_acesso'],
                    'numero_item': det.get('nItem'),
                    'codigo_produto': prod.find('cProd').text if prod.find('cProd') is not None else None,
                    'codigo_gtin': prod.find('cEAN').text if prod.find('cEAN') is not None else None,
                    'descricao': prod.find('xProd').text if prod.find('xProd') is not None else None,
                    'ncm': prod.find('NCM').text if prod.find('NCM') is not None else None,
                    'cest': prod.find('CEST').text if prod.find('CEST') is not None else None,
                    'cfop': prod.find('CFOP').text if prod.find('CFOP') is not None else None,
                    'unidade': prod.find('uCom').text if prod.find('uCom') is not None else None,
                    'quantidade': float(prod.find('qCom').text) if prod.find('qCom') is not None else 0.0,
                    'valor_unitario': float(prod.find('vUnCom').text) if prod.find('vUnCom') is not None else 0.0,
                    'valor_total': float(prod.find('vProd').text) if prod.find('vProd') is not None else 0.0,
                    'valor_item_12741': float(imposto.find('vItem12741').text) if imposto.find('vItem12741') is not None else 0.0
                }
                
                # Informações de impostos
                icms = imposto.find('ICMS/*')
                if icms is not None:
                    item['cst_icms'] = icms.find('CST').text if icms.find('CST') is not None else None
                    item['origem_icms'] = icms.find('Orig').text if icms.find('Orig') is not None else None
                
                pis = imposto.find('PIS/*')
                if pis is not None:
                    item['cst_pis'] = pis.find('CST').text if pis.find('CST') is not None else None
                
                cofins = imposto.find('COFINS/*')
                if cofins is not None:
                    item['cst_cofins'] = cofins.find('CST').text if cofins.find('CST') is not None else None
                
                itens.append(item)
            
            print(f"Processado: {file_path} - {len(itens)} itens")
            return nota, itens
            
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            return None, []
    
    def save_to_database(self, notas_data, itens_data):
        """Salva dados no banco de dados"""
        if notas_data:
            self.db.insert_notas(notas_data)
        if itens_data:
            self.db.insert_itens(itens_data)
    
    def export_to_excel(self, notas_data, itens_data, output_path):
        """Exporta dados para Excel"""
        df_notas = pd.DataFrame(notas_data)
        df_itens = pd.DataFrame(itens_data)
        
        with pd.ExcelWriter(output_path) as writer:
            df_notas.to_excel(writer, sheet_name='Notas', index=False)
            df_itens.to_excel(writer, sheet_name='Itens', index=False)