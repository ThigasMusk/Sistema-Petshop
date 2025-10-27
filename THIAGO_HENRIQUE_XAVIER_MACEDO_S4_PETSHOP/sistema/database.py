import sqlite3
import os

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    DB_NAME = os.path.join(script_dir, 'petshop.db')
    base_dir = os.path.dirname(script_dir)
    SQL_FILE = os.path.join(base_dir, 'sql', 'create_populate.sql')

except NameError:
    print("Erro ao determinar o caminho do script. Usando caminhos relativos.")
    SQL_FILE = os.path.join('..', 'sql', 'create_populate.sql')
    DB_NAME = 'petshop.db'

def criar_banco():
    if os.path.exists(DB_NAME):
        print(f"O banco de dados '{DB_NAME}' já existe. Nenhuma ação foi tomada.")
        return

    try:
        print(f"Tentando ler o arquivo SQL em: {SQL_FILE}")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print(f"Arquivo SQL lido. Criando banco em: {DB_NAME}")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()
        
        print(f"Banco de dados '{DB_NAME}' criado e populado com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Erro ao criar o banco de dados: {e}")
    except FileNotFoundError:
        print(f"Erro CRÍTICO: Arquivo SQL '{SQL_FILE}' não encontrado.")
        print("Verifique se a sua estrutura de pastas está correta (ex: /sql e /sistema no mesmo nível).")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")

if __name__ == '__main__':
    criar_banco()