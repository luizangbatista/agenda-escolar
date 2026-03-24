import sqlite3
from datetime import date, datetime
import pandas as pd
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="SisteMat", page_icon="📚", layout="centered")

TURMAS = ["6º ano A","6º ano B","7º ano","8º ano","9º ano","1ª série EM","2ª série EM"]
TIPOS_AVALIACAO = ["Testinho","Mensal","Trimestral","Suplementar"]
MONITORES = ["Luiza","Rafael","Arthur","Gabriel"]

DB_NAME = "agenda.db"

# =========================
# BANCO
# =========================
def conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    c = conn(); cur = c.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS atividades_avaliativas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT, tipo_atividade TEXT, turma TEXT)
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monitorias(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT, turma TEXT, monitor TEXT, conteudo TEXT, arquivo_drive TEXT)
    """)

    c.commit(); c.close()

# =========================
# FUNÇÕES
# =========================
def d2t(d): return d.strftime("%d/%m/%Y")
def t2d(t): return datetime.strptime(t,"%d/%m/%Y")

def inserir_atividade(d,tipo,turma):
    c=conn();c.execute("INSERT INTO atividades_avaliativas VALUES (NULL,?,?,?)",(d2t(d),tipo,turma));c.commit();c.close()

def inserir_monitoria(d,turma,monitor,cont,arq):
    c=conn();c.execute("INSERT INTO monitorias VALUES (NULL,?,?,?,?,?)",(d2t(d),turma,monitor,cont,arq));c.commit();c.close()

def deletar_atividade(id_):
    c=conn();c.execute("DELETE FROM atividades_avaliativas WHERE id=?",(id_,));c.commit();c.close()

def deletar_monitoria(id_):
    c=conn();c.execute("DELETE FROM monitorias WHERE id=?",(id_,));c.commit();c.close()

def atualizar_atividade(id_,d,tipo,turma):
    c=conn()
    c.execute("UPDATE atividades_avaliativas SET data=?,tipo_atividade=?,turma=? WHERE id=?",
              (d2t(d),tipo,turma,id_))
    c.commit();c.close()

def atualizar_monitoria(id_,d,turma,monitor,cont,arq):
    c=conn()
    c.execute("UPDATE monitorias SET data=?,turma=?,monitor=?,conteudo=?,arquivo_drive=? WHERE id=?",
              (d2t(d),turma,monitor,cont,arq,id_))
    c.commit();c.close()

def get_ativ():
    df=pd.read_sql_query("SELECT * FROM atividades_avaliativas",conn())
    if df.empty: return df
    df["data_obj"]=df["data"].apply(t2d)
    return df.sort_values("data_obj",ascending=False)

def get_mon():
    df=pd.read_sql_query("SELECT * FROM monitorias",conn())
    if df.empty: return df
    df["data_obj"]=df["data"].apply(t2d)
    return df.sort_values("data_obj",ascending=False)

# =========================
# ESTADO
# =========================
if "tela" not in st.session_state: st.session_state.tela="menu"
if "edit_id" not in st.session_state: st.session_state.edit_id=None
if "edit_tipo" not in st.session_state: st.session_state.edit_tipo=None

# =========================
# INIT
# =========================
init_db()

# =========================
# HEADER
# =========================
st.title("📚 SisteMat 📅")

# =========================
# MENU
# =========================
if st.session_state.tela=="menu":
    c1,c2,c3=st.columns(3)

    if c1.button("Cadastrar atividade avaliativa"):
        st.session_state.tela="cad_a";st.rerun()

    if c2.button("Cadastrar monitoria"):
        st.session_state.tela="cad_m";st.rerun()

    if c3.button("Consultar"):
        st.session_state.tela="cons";st.rerun()

# =========================
# CAD ATIVIDADE
# =========================
elif st.session_state.tela=="cad_a":
    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    with st.form("fa"):
        d=st.date_input("Data")
        t=st.selectbox("Turma",TURMAS)
        tp=st.selectbox("Tipo",TIPOS_AVALIACAO)
        ok=st.form_submit_button("Salvar")

    if ok:
        inserir_atividade(d,tp,t)
        st.session_state.tela="menu";st.rerun()

# =========================
# CAD MONITORIA
# =========================
elif st.session_state.tela=="cad_m":
    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    with st.form("fm"):
        d=st.date_input("Data")
        t=st.selectbox("Turma",TURMAS)
        m=st.selectbox("Monitor",MONITORES)
        c=st.text_area("Conteúdo")
        a=st.text_input("Arquivo")
        ok=st.form_submit_button("Salvar")

    if ok:
        inserir_monitoria(d,t,m,c,a)
        st.session_state.tela="menu";st.rerun()

# =========================
# CONSULTA
# =========================
elif st.session_state.tela=="cons":

    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    # =========================
    # ATIVIDADES (TABELA)
    # =========================
    st.subheader("Atividades")

    df = get_ativ()

    if df.empty:
        st.info("Nenhuma atividade cadastrada.")
    else:
        tabela = df[["data","turma","tipo_atividade"]].rename(columns={
            "data":"Data",
            "turma":"Turma",
            "tipo_atividade":"Atividade"
        })

        tabela["Alterações"] = "✏️  🗑️"

        st.dataframe(tabela, use_container_width=True, hide_index=True)

        st.markdown("### Alterar registros")

        for _,l in df.iterrows():
            col1,col2,col3,col4 = st.columns([3,3,2,2])

            col1.write(l["data"])
            col2.write(l["turma"])
            col3.write(l["tipo_atividade"])

            if col4.button("✏️", key=f"ea{l['id']}"):
                st.session_state.edit_id=l["id"]
                st.session_state.edit_tipo="a"
                st.session_state.tela="edit"
                st.rerun()

            if col4.button("🗑️", key=f"da{l['id']}"):
                deletar_atividade(l["id"])
                st.rerun()

    st.markdown("---")

    # =========================
    # MONITORIAS
    # =========================
    st.subheader("Monitorias")

    df = get_mon()

    if df.empty:
        st.info("Nenhuma monitoria cadastrada.")
    else:
        for _,l in df.iterrows():
            c1,c2,c3 = st.columns([6,1,1])

            c1.write(f"{l['data']} • {l['turma']} • {l['monitor']} — {l['conteudo']}")

            if c2.button("✏️", key=f"em{l['id']}"):
                st.session_state.edit_id=l["id"]
                st.session_state.edit_tipo="m"
                st.session_state.tela="edit"
                st.rerun()

            if c3.button("🗑️", key=f"dm{l['id']}"):
                deletar_monitoria(l["id"])
                st.rerun()

            st.markdown("---")

# =========================
# EDITAR
# =========================
elif st.session_state.tela=="edit":

    if st.button("⬅ Voltar"):
        st.session_state.tela="cons";st.rerun()

    if st.session_state.edit_tipo=="a":
        df=get_ativ()
        l=df[df["id"]==st.session_state.edit_id].iloc[0]

        with st.form("editA"):
            d=st.date_input("Data",value=l["data_obj"])
            t=st.selectbox("Turma",TURMAS,index=TURMAS.index(l["turma"]))
            tp=st.selectbox("Tipo",TIPOS_AVALIACAO,index=TIPOS_AVALIACAO.index(l["tipo_atividade"]))
            ok=st.form_submit_button("Salvar")

        if ok:
            atualizar_atividade(l["id"],d,tp,t)
            st.session_state.tela="cons";st.rerun()

    if st.session_state.edit_tipo=="m":
        df=get_mon()
        l=df[df["id"]==st.session_state.edit_id].iloc[0]

        with st.form("editM"):
            d=st.date_input("Data",value=l["data_obj"])
            t=st.selectbox("Turma",TURMAS,index=TURMAS.index(l["turma"]))
            m=st.selectbox("Monitor",MONITORES,index=MONITORES.index(l["monitor"]))
            c=st.text_area("Conteúdo",value=l["conteudo"])
            a=st.text_input("Arquivo",value=l["arquivo_drive"])
            ok=st.form_submit_button("Salvar")

        if ok:
            atualizar_monitoria(l["id"],d,t,m,c,a)
            st.session_state.tela="cons";st.rerun()