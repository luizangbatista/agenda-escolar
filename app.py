import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SisteMat", page_icon="📚", layout="centered")

st.markdown("""
<style>
div.stButton > button {
    padding: 0.25rem 0.55rem;
    font-size: 14px;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
}
hr {
    margin: 8px 0;
    opacity: 0.35;
}
</style>
""", unsafe_allow_html=True)

TURMAS = [
    "6º ano A",
    "6º ano B",
    "7º ano",
    "8º ano",
    "9º ano",
    "1ª série EM",
    "2ª série EM",
]

TIPOS_AVALIACAO = [
    "Testinho",
    "Mensal",
    "Trimestral",
    "Suplementar",
]

MONITORES = [
    "Luiza",
    "Rafael",
    "Arthur",
    "Gabriel",
]

DB_NAME = "agenda.db"


# =========================
# BANCO
# =========================
def conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    c = conn()
    cur = c.cursor()

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

    c.commit()
    c.close()


def d2t(d):
    return d.strftime("%d/%m/%Y")


def t2d(t):
    return datetime.strptime(t, "%d/%m/%Y")


# =========================
# CRUD
# =========================
def inserir_atividade(d, tipo, turma):
    c = conn()
    c.execute(
        "INSERT INTO atividades_avaliativas (data, tipo_atividade, turma) VALUES (?, ?, ?)",
        (d2t(d), tipo, turma),
    )
    c.commit()
    c.close()


def inserir_monitoria(d, turma, monitor, conteudo, arquivo):
    c = conn()
    c.execute(
        "INSERT INTO monitorias (data, turma, monitor, conteudo, arquivo_drive) VALUES (?, ?, ?, ?, ?)",
        (d2t(d), turma, monitor, conteudo, arquivo),
    )
    c.commit()
    c.close()


def deletar_atividade(id_):
    c = conn()
    c.execute("DELETE FROM atividades_avaliativas WHERE id = ?", (id_,))
    c.commit()
    c.close()


def deletar_monitoria(id_):
    c = conn()
    c.execute("DELETE FROM monitorias WHERE id = ?", (id_,))
    c.commit()
    c.close()


def atualizar_atividade(id_, d, tipo, turma):
    c = conn()
    c.execute(
        "UPDATE atividades_avaliativas SET data = ?, tipo_atividade = ?, turma = ? WHERE id = ?",
        (d2t(d), tipo, turma, id_),
    )
    c.commit()
    c.close()


def buscar_atividades():
    c = conn()
    df = pd.read_sql_query("SELECT * FROM atividades_avaliativas", c)
    c.close()

    if df.empty:
        return df

    df["data_obj"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    return df.sort_values("data_obj", ascending=False)


def buscar_monitorias():
    c = conn()
    df = pd.read_sql_query("SELECT * FROM monitorias", c)
    c.close()

    if df.empty:
        return df

    df["data_obj"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    return df.sort_values("data_obj", ascending=False)


# =========================
# ESTADO
# =========================
if "tela" not in st.session_state:
    st.session_state.tela = "menu"

if "modo_edicao_ativ" not in st.session_state:
    st.session_state.modo_edicao_ativ = False

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if "edit_tipo" not in st.session_state:
    st.session_state.edit_tipo = None


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
if st.session_state.tela == "menu":
    c1, c2, c3 = st.columns(3)

    if c1.button("Cadastrar atividade avaliativa"):
        st.session_state.tela = "cad_a"
        st.rerun()

    if c2.button("Cadastrar monitoria"):
        st.session_state.tela = "cad_m"
        st.rerun()

    if c3.button("Consultar"):
        st.session_state.tela = "cons"
        st.rerun()


# =========================
# CADASTRO ATIVIDADE
# =========================
elif st.session_state.tela == "cad_a":
    if st.button("⬅ Voltar"):
        st.session_state.tela = "menu"
        st.rerun()

    st.subheader("Cadastrar atividade avaliativa")

    with st.form("form_atividade"):
        d = st.date_input("Data")
        turma = st.selectbox("Turma", TURMAS)
        tipo = st.selectbox("Tipo", TIPOS_AVALIACAO)
        ok = st.form_submit_button("Salvar")

    if ok:
        inserir_atividade(d, tipo, turma)
        st.session_state.tela = "menu"
        st.rerun()


# =========================
# CADASTRO MONITORIA
# =========================
elif st.session_state.tela == "cad_m":
    if st.button("⬅ Voltar"):
        st.session_state.tela = "menu"
        st.rerun()

    st.subheader("Cadastrar monitoria")

    with st.form("form_monitoria"):
        d = st.date_input("Data")
        turma = st.selectbox("Turma", TURMAS)
        monitor = st.selectbox("Monitor", MONITORES)
        conteudo = st.text_area("Conteúdo")
        arquivo = st.text_input("Arquivo do Drive")
        ok = st.form_submit_button("Salvar")

    if ok:
        inserir_monitoria(d, turma, monitor, conteudo, arquivo)
        st.session_state.tela = "menu"
        st.rerun()


# =========================
# CONSULTA
# =========================
elif st.session_state.tela == "cons":
    if st.button("⬅ Voltar"):
        st.session_state.tela = "menu"
        st.session_state.modo_edicao_ativ = False
        st.rerun()

    st.subheader("Filtros")

    col1, col2 = st.columns(2)
    data_ini = col1.date_input("Data inicial", value=None)
    data_fim = col2.date_input("Data final", value=None)

    col3, col4 = st.columns(2)
    filtro_turma = col3.selectbox("Turma", ["Todas"] + TURMAS)
    filtro_monitor = col4.selectbox("Monitor", ["Todos"] + MONITORES)

    # =========================
    # ATIVIDADES
    # =========================
    st.subheader("Atividades avaliativas")

    df_ativ = buscar_atividades()

    if not df_ativ.empty:
        if filtro_turma != "Todas":
            df_ativ = df_ativ[df_ativ["turma"] == filtro_turma]

        if data_ini is not None:
            df_ativ = df_ativ[df_ativ["data_obj"] >= pd.to_datetime(data_ini)]

        if data_fim is not None:
            df_ativ = df_ativ[df_ativ["data_obj"] <= pd.to_datetime(data_fim)]

    if df_ativ.empty:
        st.info("Nenhuma atividade avaliativa encontrada.")
    else:
        tabela = df_ativ[["data", "turma", "tipo_atividade"]].copy()
        tabela.columns = ["Data", "Turma", "Atividade"]

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
        )

        if not st.session_state.modo_edicao_ativ:
            if st.button("✏️ Alterar registros de atividades"):
                st.session_state.modo_edicao_ativ = True
                st.rerun()

    if st.session_state.modo_edicao_ativ:
        st.markdown("### Alterar atividades avaliativas")

        if st.button("⬅ Fechar alteração de atividades"):
            st.session_state.modo_edicao_ativ = False
            st.rerun()

        if df_ativ.empty:
            st.info("Nenhuma atividade para alterar com os filtros atuais.")
        else:
            for _, linha in df_ativ.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2.2, 2.5, 2.2, 1, 1])

                c1.write(linha["data"])
                c2.write(linha["turma"])
                c3.write(linha["tipo_atividade"])

                if c4.button("✏️", key=f"edit_a_{linha['id']}"):
                    st.session_state.edit_id = linha["id"]
                    st.session_state.edit_tipo = "atividade"
                    st.session_state.tela = "edit"
                    st.rerun()

                if c5.button("🗑️", key=f"del_a_{linha['id']}"):
                    deletar_atividade(linha["id"])
                    st.rerun()

    st.markdown("---")

    # =========================
    # MONITORIAS
    # =========================
    st.subheader("Monitorias")

    df_mon = buscar_monitorias()

    if not df_mon.empty:
        if filtro_turma != "Todas":
            df_mon = df_mon[df_mon["turma"] == filtro_turma]

        if filtro_monitor != "Todos":
            df_mon = df_mon[df_mon["monitor"] == filtro_monitor]

        if data_ini is not None:
            df_mon = df_mon[df_mon["data_obj"] >= pd.to_datetime(data_ini)]

        if data_fim is not None:
            df_mon = df_mon[df_mon["data_obj"] <= pd.to_datetime(data_fim)]

    if df_mon.empty:
        st.info("Nenhuma monitoria encontrada.")
    else:
        for _, linha in df_mon.iterrows():

            col1, col2 = st.columns([10, 1], gap="small")

            col1.markdown(f"**{linha['data']} | {linha['turma']} | {linha['monitor']}**")

            with col2:
                if st.button("🗑️", key=f"del_m_{linha['id']}", use_container_width=True):
                    deletar_monitoria(linha["id"])
                st.rerun()

    # 👇 FORA DO with col2 (IMPORTANTE)
            st.markdown(f"CONTEÚDO: {linha['conteudo']}")

            arquivo = (linha["arquivo_drive"] or "").strip()
            if arquivo:
                st.markdown(f"ARQUIVO: {arquivo}")

            st.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)


# =========================
# EDITAR ATIVIDADE
# =========================
elif st.session_state.tela == "edit":
    if st.button("⬅ Voltar"):
        st.session_state.tela = "cons"
        st.rerun()

    if st.session_state.edit_tipo == "atividade":
        df = buscar_atividades()

        if df.empty or st.session_state.edit_id not in df["id"].values:
            st.warning("Atividade não encontrada.")
        else:
            linha = df[df["id"] == st.session_state.edit_id].iloc[0]

            st.subheader("Editar atividade avaliativa")

            with st.form("edit_atividade"):
                d = st.date_input("Data", value=linha["data_obj"].date())
                turma = st.selectbox("Turma", TURMAS, index=TURMAS.index(linha["turma"]))
                tipo = st.selectbox("Tipo", TIPOS_AVALIACAO, index=TIPOS_AVALIACAO.index(linha["tipo_atividade"]))
                ok = st.form_submit_button("Salvar")

            if ok:
                atualizar_atividade(linha["id"], d, tipo, turma)
                st.session_state.tela = "cons"
                st.rerun()