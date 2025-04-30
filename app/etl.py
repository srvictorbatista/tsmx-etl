#!/usr/bin/env python3
import os
import shutil
import pandas as pd
import psycopg2
from pathlib import Path
from psycopg2.extras import execute_batch
from datetime import datetime

pd.set_option('future.no_silent_downcasting', True)
UPLOAD_DIR = Path("backups")
UPLOAD_DIR.mkdir(exist_ok=True)


def conectar_banco():
    return psycopg2.connect(
        dbname="tsmx_etl",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )



def inserir_oscar(ceremony, year, conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tbl_oscar (ceremony, year)
            VALUES (%s, %s)
            ON CONFLICT (ceremony) DO NOTHING
            RETURNING id;
        """, (ceremony, year))
        result = cursor.fetchone()
        conn.commit()
        if result:
            return result[0]
        cursor.execute("SELECT id FROM tbl_oscar WHERE ceremony = %s", (ceremony,))
        return cursor.fetchone()[0]

def inserir_class(description, conn):
    description = description.strip() if description else "Classe desconhecida"
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM tbl_class WHERE description = %s", (description,))
        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.execute("""
            INSERT INTO tbl_class (description)
            VALUES (%s)
            RETURNING id;
        """, (description,))
        conn.commit()
        return cursor.fetchone()[0]

def inserir_category(description, conn):
    description = description.strip() if description else "Categoria desconhecida"
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tbl_category (description)
            VALUES (%s)
            ON CONFLICT(description) DO NOTHING
            RETURNING id;
        """, (description,))
        result = cursor.fetchone()
        conn.commit()
        if result:
            return result[0]
        cursor.execute("SELECT id FROM tbl_category WHERE description = %s", (description,))
        return cursor.fetchone()[0]

def inserir_movie(title, conn):
    title = title.strip() if title else "Título desconhecido"
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM tbl_movie WHERE title = %s", (title,))
        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.execute("""
            INSERT INTO tbl_movie (title)
            VALUES (%s)
            RETURNING id;
        """, (title,))
        conn.commit()
        return cursor.fetchone()[0]

def inserir_nominee(oscar_id, class_id, category_id, movie_id, name, nominees, winner, detail, note, conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO tbl_nominees (oscar_id, class_id, category_id, movie_id, name, nominees, winner, detail, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (oscar_id, class_id, category_id, movie_id, name, nominees, winner, detail, note))
        conn.commit()

def normalizar_dataframe(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    for col in ['note', 'detail', 'nominees', 'name', 'movie', 'category', 'class']:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    df['winner'] = df['winner'].fillna(False)
    df['winner'] = df['winner'].apply(lambda x: str(x).strip().lower() in ['true', '1', 'yes'])
    obrigatorias = ["ceremony", "year", "class", "category", "movie", "winner"]
    for col in obrigatorias:
        if col not in df.columns:
            raise Exception(f"🛑 Coluna obrigatória ausente: {col}")
    return df

def receber_arquivo():
    print("🔍 Informe o arquivo que deseja importar:")
    caminho = input("📁 Caminho do arquivo: ").strip()
    caminho_str = str(caminho)
    if not os.path.exists(caminho_str):
        print("❌ Arquivo não encontrado.")
        return None
    if not caminho_str.lower().endswith((".csv", ".xls", ".xlsx")):
        print("❌ Apenas arquivos .csv, .xls e .xlsx são suportados neste processo.")
        return None
    destino = UPLOAD_DIR / os.path.basename(caminho_str)
    shutil.copy(caminho_str, destino)
    print(f"✅ Arquivo copiado para: {destino}")
    return destino

def visualizar_arquivo(caminho):
    try:
        print("\n📄 Lendo o arquivo...")
        df = carregar_arquivo(caminho)
        print("📑 Primeiras linhas do arquivo:")
        print(df.head())
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo: {e}")

def carregar_arquivo(caminho):
    caminho_str = str(caminho)
    if caminho_str.lower().endswith(".csv"):
        try:
            return pd.read_csv(caminho_str, sep=None, engine='python', encoding='utf-8', quotechar='"', on_bad_lines='skip')
        except UnicodeDecodeError:
            return pd.read_csv(caminho_str, sep=None, engine='python', encoding='latin1', quotechar='"', on_bad_lines='skip')
    elif caminho_str.lower().endswith((".xls", ".xlsx")):
        return pd.read_excel(caminho_str, engine='openpyxl' if caminho_str.endswith('xlsx') else 'xlrd')
    else:
        raise Exception("Formato de arquivo não suportado.")

def salvar_log_erros(nome_arquivo, rejeitados):
    log_path = UPLOAD_DIR / f"{Path(nome_arquivo).stem}.log"
    with open(log_path, 'w', encoding='utf-8') as log_file:
        for item in rejeitados:
            log_file.write(f"Linha {item['linha']} - Motivo: {item['motivo']}\n")
            log_file.write(f"Dados: {item['dados']}\n")
            log_file.write("-" * 80 + "\n")
    return log_path

def exibir_resumo(importados, rejeitados, nome_arquivo):
    print("\n📊 RESUMO DA IMPORTAÇÃO:")
    print(f"✅ Total de registros importados: {len(importados)}")
    print(f"⚠️ Total de registros rejeitados: {len(rejeitados)}")

    if rejeitados:
        log_path = salvar_log_erros(nome_arquivo, rejeitados)
        print(f"\n\n📝 Lista de registros rejeitados salvo em: {log_path}")
        visualizar = input("👀 Deseja visualizar este log agora? (S/N): ").strip().lower()
        if visualizar != 'n':
            os.system(f"cat {log_path}")

def processar_etl(df, nome_arquivo):
    df = normalizar_dataframe(df)
    conn = conectar_banco()
    importados = []
    rejeitados = []

    print("\n⏳ Processando ETL. Aguarde...")

    for index, row in df.iterrows():
        try:
            row = row.apply(lambda x: x.encode('utf-8', errors='replace').decode('utf-8') if isinstance(x, str) else x)

            oscar_id = inserir_oscar(int(row['ceremony']), int(row['year']), conn)
            class_id = inserir_class(row['class'], conn)
            category_id = inserir_category(row['category'], conn)
            movie_id = inserir_movie(row['movie'], conn)

            inserir_nominee(
                oscar_id,
                class_id,
                category_id,
                movie_id,
                row.get('name', ''),
                row.get('nominees', ''),
                row.get('winner', False),
                row.get('detail', ''),
                row.get('note', ''),
                conn
            )
            importados.append(index)
        except Exception as e:
            conn.rollback()
            rejeitados.append({
                "linha": index + 2,
                "dados": row.to_dict(),
                "motivo": str(e)
            })

    conn.close()
    exibir_resumo(importados, rejeitados, nome_arquivo)

def executar():
    caminho = receber_arquivo()
    if caminho:
        visualizar_arquivo(caminho)
        try:
            df = carregar_arquivo(caminho)
            processar_etl(df, os.path.basename(caminho))
        except Exception as e:
            print(f"❌ Erro durante o processamento: {e}")



if __name__ == "__main__":
    executar()
