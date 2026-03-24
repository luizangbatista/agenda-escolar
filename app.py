import sqlite3
from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SisteMat", page_icon="📚", layout="centered")

# =========================
# CSS ULTRA CLEAN
# =========================
st.markdown("""
<style>

/* botão sem fundo */
div.stButton > button {
    background: none;
    border: none;
    padding: 0;
    font-size: 18px;
}

/* remove hover feio */
div.stButton > button:hover {
    background: none;
    transform: scale(1.1);
}

/* reduz espaço geral */
.block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
}

/* linha divisória mais suave */
hr {
    margin: 6px 0;
    opacity: 0.3;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LISTAS
# =========================
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
    c = conn()
    c.execute("CREATE TABLE IF NOT EXISTS atividades_avaliativas(id INTEGER PRIMARY KEY, data TEXT, tipo_atividade TEXT, turma TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS monitorias(id INTEGER PRIMARY KEY, data TEXT, turma TEXT, monitor TEXT, conteudo TEXT, arquivo_drive TEXT)")
    c.commit(); c.close()

def d2t(d): return d.strftime("%d/%m/%Y")
def t2d(t): return datetime.strptime(t,"%d/%m/%Y")

# =========================
# CRUD
# =========================
def inserir_atividade(d,tipo,turma):
    conn().execute("INSERT INTO atividades_avaliativas VALUES(NULL,?,?,?)",(d2t(d),tipo,turma)).connection.commit()

def inserir_monitoria(d,t,m,c,a):
    conn().execute("INSERT INTO monitorias VALUES(NULL,?,?,?,?,?)",(d2t(d),t,m,c,a)).connection.commit()

def deletar_atividade(id_):
    conn().execute("DELETE FROM atividades_avaliativas WHERE id=?",(id_,)).connection.commit()

def deletar_monitoria(id_):
    conn().execute("DELETE FROM monitorias WHERE id=?",(id_,)).connection.commit()

def atualizar_atividade(id_,d,tipo,turma):
    conn().execute("UPDATE atividades_avaliativas SET data=?,tipo_atividade=?,turma=? WHERE id=?",(d2t(d),tipo,turma,id_)).connection.commit()

def atualizar_monitoria(id_,d,t,m,c,a):
    conn().execute("UPDATE monitorias SET data=?,turma=?,monitor=?,conteudo=?,arquivo_drive=? WHERE id=?",(d2t(d),t,m,c,a,id_)).connection.commit()

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
if "modo_edicao" not in st.session_state: st.session_state.modo_edicao=False
if "edit_id" not in st.session_state: st.session_state.edit_id=None
if "edit_tipo" not in st.session_state: st.session_state.edit_tipo=None

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
# CADASTROS
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
        st.session_state.tela="menu"
        st.rerun()

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
        st.session_state.tela="menu"
        st.rerun()

# =========================
# CONSULTA
# =========================
elif st.session_state.tela=="cons":

    if st.button("⬅ Voltar"):
        st.session_state.tela="menu";st.rerun()

    st.subheader("Monitorias")

    df = get_mon()

    if df.empty:
        st.info("Nenhuma monitoria encontrada.")
    else:
        for _, l in df.iterrows():

            # LINHA PRINCIPAL COM BOTÕES
            col1, col2 = st.columns([9,1])

            col1.markdown(f"**{l['data']} | {l['turma']} | {l['monitor']}**")

            # BOTÕES NA MESMA LINHA DO TÍTULO
            with col2:
                cols = st.columns(2)

                if cols[0].button("✏️", key=f"em{l['id']}", use_container_width=True):
                    st.session_state.edit_id=l["id"]
                    st.session_state.edit_tipo="m"
                    st.session_state.tela="edit"
                    st.rerun()

                if cols[1].button("🗑️", key=f"dm{l['id']}", use_container_width=True):
                    deletar_monitoria(l["id"])
                    st.rerun()

            # CONTEÚDO
            st.markdown(f"CONTEÚDO: {l['conteudo']}")

            if l["arquivo_drive"]:
                st.markdown(f"ARQUIVO: {l['arquivo_drive']}")

            st.markdown("<hr>", unsafe_allow_html=True)

# =========================
# EDIT
# =========================
elif st.session_state.tela=="edit":

    if st.button("⬅ Voltar"):
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