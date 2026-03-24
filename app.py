import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="SisteMat", page_icon="📚", layout="centered")

TURMAS = [
    "6º ano A","6º ano B","7º ano","8º ano","9º ano","1ª série EM","2ª série EM",
]

TIPOS_AVALIACAO = ["Testinho","Mensal","Trimestral","Suplementar"]

MONITORES = ["Luiza","Rafael","Arthur","Gabriel"]

MESES = {
    "Todos":0,"Janeiro":1,"Fevereiro":2,"Março":3,"Abril":4,
    "Maio":5,"Junho":6,"Julho":7,"Agosto":8,"Setembro":9,
    "Outubro":10,"Novembro":11,"Dezembro":12,
}

DB_NAME = "agenda.db"

# =========================
# BANCO
# =========================
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS atividades_avaliativas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo_atividade TEXT,
            turma TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monitorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            turma TEXT,
            monitor TEXT,
            conteudo TEXT,
            arquivo_drive TEXT
        )
    """)

    conn.commit()
    conn.close()

# =========================
# FUNÇÕES
# =========================
def data_para_texto(d): return d.strftime("%d/%m/%Y")
def texto_para_data(t): return datetime.strptime(t, "%d/%m/%Y")

# ATIVIDADE
def inserir_atividade(d,tipo,turma):
    conn=get_connection();cur=conn.cursor()
    cur.execute("INSERT INTO atividades_avaliativas (data,tipo_atividade,turma) VALUES (?,?,?)",
                (data_para_texto(d),tipo,turma))
    conn.commit();conn.close()

def deletar_atividade(id_):
    conn=get_connection();cur=conn.cursor()
    cur.execute("DELETE FROM atividades_avaliativas WHERE id=?",(id_,))
    conn.commit();conn.close()

def atualizar_atividade(id_,d,tipo,turma):
    conn=get_connection();cur=conn.cursor()
    cur.execute("UPDATE atividades_avaliativas SET data=?,tipo_atividade=?,turma=? WHERE id=?",
                (data_para_texto(d),tipo,turma,id_))
    conn.commit();conn.close()

def buscar_atividades():
    conn=get_connection()
    df=pd.read_sql_query("SELECT * FROM atividades_avaliativas",conn)
    conn.close()
    if not df.empty: df["data_obj"]=df["data"].apply(texto_para_data)
    return df

# MONITORIA
def inserir_monitoria(d,turma,monitor,conteudo,arquivo):
    conn=get_connection();cur=conn.cursor()
    cur.execute("INSERT INTO monitorias (data,turma,monitor,conteudo,arquivo_drive) VALUES (?,?,?,?,?)",
                (data_para_texto(d),turma,monitor,conteudo,arquivo))
    conn.commit();conn.close()

def deletar_monitoria(id_):
    conn=get_connection();cur=conn.cursor()
    cur.execute("DELETE FROM monitorias WHERE id=?",(id_,))
    conn.commit();conn.close()

def atualizar_monitoria(id_,d,turma,monitor,conteudo,arquivo):
    conn=get_connection();cur=conn.cursor()
    cur.execute("""UPDATE monitorias 
                   SET data=?,turma=?,monitor=?,conteudo=?,arquivo_drive=? 
                   WHERE id=?""",
                (data_para_texto(d),turma,monitor,conteudo,arquivo,id_))
    conn.commit();conn.close()

def buscar_monitorias():
    conn=get_connection()
    df=pd.read_sql_query("SELECT * FROM monitorias",conn)
    conn.close()
    if not df.empty: df["data_obj"]=df["data"].apply(texto_para_data)
    return df

# =========================
# ESTADO
# =========================
if "tela" not in st.session_state: st.session_state.tela="menu"
if "msg" not in st.session_state: st.session_state.msg=""
if "edit_id" not in st.session_state: st.session_state.edit_id=None
if "edit_tipo" not in st.session_state: st.session_state.edit_tipo=None

# =========================
# INIT
# =========================
init_db()

# =========================
# UI
# =========================
st.title("📚 SisteMat")

if st.session_state.msg:
    st.success(st.session_state.msg)
    st.session_state.msg=""

# =========================
# MENU
# =========================
if st.session_state.tela=="menu":
    col1,col2,col3=st.columns(3)
    if col1.button("Cadastrar atividade"):
        st.session_state.tela="cad_atividade";st.rerun()
    if col2.button("Cadastrar monitoria"):
        st.session_state.tela="cad_monitoria";st.rerun()
    if col3.button("Consultar"):
        st.session_state.tela="consultar";st.rerun()

# =========================
# CAD ATIVIDADE
# =========================
elif st.session_state.tela=="cad_atividade":
    st.subheader("Cadastrar atividade")

    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    with st.form("f"):
        d=st.date_input("Data")
        turma=st.selectbox("Turma",TURMAS)
        tipo=st.selectbox("Tipo",TIPOS_AVALIACAO)
        ok=st.form_submit_button("Salvar")

    if ok:
        inserir_atividade(d,tipo,turma)
        st.session_state.msg="Salvo"
        st.session_state.tela="menu";st.rerun()

# =========================
# CAD MONITORIA
# =========================
elif st.session_state.tela=="cad_monitoria":
    st.subheader("Cadastrar monitoria")

    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    with st.form("f2"):
        d=st.date_input("Data")
        turma=st.selectbox("Turma",TURMAS)
        monitor=st.selectbox("Monitor",MONITORES)
        cont=st.text_area("Conteúdo")
        arq=st.text_input("Arquivo")
        ok=st.form_submit_button("Salvar")

    if ok:
        inserir_monitoria(d,turma,monitor,cont,arq)
        st.session_state.msg="Salvo"
        st.session_state.tela="menu";st.rerun()

# =========================
# CONSULTA
# =========================
elif st.session_state.tela=="consultar":

    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    tipo=st.selectbox("Seção",["Tudo","Atividades","Monitorias"])

    # ATIVIDADES
    if tipo in ["Tudo","Atividades"]:
        st.subheader("Atividades")
        df=buscar_atividades()

        for _,l in df.iterrows():
            st.write(f"{l['data']} - {l['turma']} - {l['tipo_atividade']}")
            c1,c2=st.columns(2)

            if c1.button("✏️ Editar",key=f"ea{l['id']}"):
                st.session_state.edit_id=l["id"]
                st.session_state.edit_tipo="atividade"
                st.session_state.tela="editar";st.rerun()

            if c2.button("🗑 Excluir",key=f"da{l['id']}"):
                deletar_atividade(l["id"])
                st.rerun()

    # MONITORIAS
    if tipo in ["Tudo","Monitorias"]:
        st.subheader("Monitorias")
        df=buscar_monitorias()

        for _,l in df.iterrows():
            st.write(f"{l['data']} - {l['turma']} - {l['monitor']}")
            st.write(l["conteudo"])

            c1,c2=st.columns(2)

            if c1.button("✏️ Editar",key=f"em{l['id']}"):
                st.session_state.edit_id=l["id"]
                st.session_state.edit_tipo="monitoria"
                st.session_state.tela="editar";st.rerun()

            if c2.button("🗑 Excluir",key=f"dm{l['id']}"):
                deletar_monitoria(l["id"])
                st.rerun()

            st.markdown("---")

# =========================
# EDITAR
# =========================
elif st.session_state.tela=="editar":

    if st.button("⬅ Voltar"):
        st.session_state.tela="consultar";st.rerun()

    if st.session_state.edit_tipo=="atividade":
        df=buscar_atividades()
        linha=df[df["id"]==st.session_state.edit_id].iloc[0]

        with st.form("editA"):
            d=st.date_input("Data",value=linha["data_obj"])
            turma=st.selectbox("Turma",TURMAS,index=TURMAS.index(linha["turma"]))
            tipo=st.selectbox("Tipo",TIPOS_AVALIACAO,index=TIPOS_AVALIACAO.index(linha["tipo_atividade"]))
            ok=st.form_submit_button("Salvar")

        if ok:
            atualizar_atividade(st.session_state.edit_id,d,tipo,turma)
            st.session_state.tela="consultar";st.rerun()

    if st.session_state.edit_tipo=="monitoria":
        df=buscar_monitorias()
        linha=df[df["id"]==st.session_state.edit_id].iloc[0]

        with st.form("editM"):
            d=st.date_input("Data",value=linha["data_obj"])
            turma=st.selectbox("Turma",TURMAS,index=TURMAS.index(linha["turma"]))
            monitor=st.selectbox("Monitor",MONITORES,index=MONITORES.index(linha["monitor"]))
            cont=st.text_area("Conteúdo",value=linha["conteudo"])
            arq=st.text_input("Arquivo",value=linha["arquivo_drive"])
            ok=st.form_submit_button("Salvar")

        if ok:
            atualizar_monitoria(st.session_state.edit_id,d,turma,monitor,cont,arq)
            st.session_state.tela="consultar";st.rerun()