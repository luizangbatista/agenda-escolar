import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="SisteMat",
    page_icon="📚",
    layout="centered",
)

# =========================
# LISTAS FIXAS DO APP
# =========================
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

MESES = {
    "Todos": 0,
    "Janeiro": 1,
    "Fevereiro": 2,
    "Março": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}

DB_NAME = "agenda.db"


# =========================
# BANCO DE DADOS
# =========================
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS atividades_avaliativas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo_atividade TEXT NOT NULL,
            turma TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monitorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            turma TEXT NOT NULL,
            monitor TEXT,
            conteudo TEXT NOT NULL,
            arquivo_drive TEXT
        )
    """)

    # Migrações simples para bancos antigos
    colunas_monitorias = [col[1] for col in cur.execute("PRAGMA table_info(monitorias)").fetchall()]

    if "monitor" not in colunas_monitorias:
        cur.execute("ALTER TABLE monitorias ADD COLUMN monitor TEXT")

    if "arquivo_drive" not in colunas_monitorias:
        cur.execute("ALTER TABLE monitorias ADD COLUMN arquivo_drive TEXT")

    conn.commit()
    conn.close()


# =========================
# FUNÇÕES AUXILIARES
# =========================
def data_para_texto(data_obj):
    return data_obj.strftime("%d/%m/%Y")


def texto_para_data(data_texto):
    return datetime.strptime(data_texto, "%d/%m/%Y")


def normalizar_turma(valor):
    mapa = {
        "8o": "8º ano",
        "8º": "8º ano",
        "8 ano": "8º ano",
        "7o": "7º ano",
        "7º": "7º ano",
        "7 ano": "7º ano",
        "6A": "6º ano A",
        "6º A": "6º ano A",
        "6 ano A": "6º ano A",
        "6B": "6º ano B",
        "6º B": "6º ano B",
        "6 ano B": "6º ano B",
        "1ª série": "1ª série EM",
        "1EM": "1ª série EM",
        "1º EM": "1ª série EM",
        "2ª série": "2ª série EM",
        "2EM": "2ª série EM",
        "2º EM": "2ª série EM",
    }
    return mapa.get(valor, valor)


def corrigir_dados_antigos():
    conn = get_connection()
    cur = conn.cursor()

    # Atividades
    linhas = cur.execute("SELECT id, turma FROM atividades_avaliativas").fetchall()
    for linha_id, turma in linhas:
        turma_corrigida = normalizar_turma(turma)
        if turma_corrigida != turma:
            cur.execute(
                "UPDATE atividades_avaliativas SET turma = ? WHERE id = ?",
                (turma_corrigida, linha_id),
            )

    # Monitorias
    linhas = cur.execute("SELECT id, turma FROM monitorias").fetchall()
    for linha_id, turma in linhas:
        turma_corrigida = normalizar_turma(turma)
        if turma_corrigida != turma:
            cur.execute(
                "UPDATE monitorias SET turma = ? WHERE id = ?",
                (turma_corrigida, linha_id),
            )

    conn.commit()
    conn.close()


def inserir_atividade(data_atividade, tipo_atividade, turma):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO atividades_avaliativas (data, tipo_atividade, turma)
        VALUES (?, ?, ?)
    """, (data_para_texto(data_atividade), tipo_atividade, turma))
    conn.commit()
    conn.close()


def inserir_monitoria(data_monitoria, turma, monitor, conteudo, arquivo_drive):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO monitorias (data, turma, monitor, conteudo, arquivo_drive)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data_para_texto(data_monitoria),
        turma,
        monitor,
        conteudo.strip(),
        arquivo_drive.strip(),
    ))
    conn.commit()
    conn.close()


def buscar_atividades():
    conn = get_connection()
    query = "SELECT id, data, tipo_atividade, turma FROM atividades_avaliativas"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        df["data_obj"] = df["data"].apply(texto_para_data)
    return df


def buscar_monitorias():
    conn = get_connection()
    query = "SELECT id, data, turma, monitor, conteudo, arquivo_drive FROM monitorias"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        df["data_obj"] = df["data"].apply(texto_para_data)
    return df


def filtrar_por_mes(df, nome_mes):
    if df.empty or nome_mes == "Todos":
        return df
    numero_mes = MESES[nome_mes]
    return df[df["data_obj"].dt.month == numero_mes]


def formatar_dataframe_atividades(df):
    if df.empty:
        return df

    df = df.copy()
    df = df.sort_values("data_obj", ascending=False)
    return df[["data", "tipo_atividade", "turma"]].rename(
        columns={
            "data": "Data",
            "tipo_atividade": "Tipo de atividade",
            "turma": "Turma",
        }
    )


# =========================
# ESTADO DA TELA
# =========================
if "tela" not in st.session_state:
    st.session_state.tela = "menu"

if "mensagem" not in st.session_state:
    st.session_state.mensagem = ""


# =========================
# INICIALIZAÇÃO
# =========================
init_db()
corrigir_dados_antigos()


# =========================
# CABEÇALHO
# =========================
st.title("📚 SisteMat")

if st.session_state.mensagem:
    st.success(st.session_state.mensagem)
    st.session_state.mensagem = ""


# =========================
# MENU PRINCIPAL
# =========================
if st.session_state.tela == "menu":
    st.subheader("Menu principal")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Cadastrar atividade", use_container_width=True):
            st.session_state.tela = "cad_atividade"
            st.rerun()

    with col2:
        if st.button("Cadastrar monitoria", use_container_width=True):
            st.session_state.tela = "cad_monitoria"
            st.rerun()

    with col3:
        if st.button("Consultar", use_container_width=True):
            st.session_state.tela = "consultar"
            st.rerun()


# =========================
# CADASTRO DE ATIVIDADE
# =========================
elif st.session_state.tela == "cad_atividade":
    st.subheader("Cadastrar atividade avaliativa")

    with st.form("form_atividade"):
        data_atividade = st.date_input("Data", value=date.today())

        turma = st.selectbox(
            "Turma",
            TURMAS,
            index=None,
            placeholder="Selecione a turma",
        )

        tipo_atividade = st.selectbox(
            "Tipo de atividade avaliativa",
            TIPOS_AVALIACAO,
            index=None,
            placeholder="Selecione o tipo",
        )

        col1, col2 = st.columns(2)
        salvar = col1.form_submit_button("Salvar", use_container_width=True)
        voltar = col2.form_submit_button("Voltar ao menu", use_container_width=True)

    if voltar:
        st.session_state.tela = "menu"
        st.rerun()

    if salvar:
        if not turma or not tipo_atividade:
            st.error("Preencha todos os campos.")
        else:
            inserir_atividade(
                data_atividade=data_atividade,
                tipo_atividade=tipo_atividade,
                turma=turma,
            )
            st.session_state.mensagem = "Atividade cadastrada com sucesso."
            st.session_state.tela = "menu"
            st.rerun()


# =========================
# CADASTRO DE MONITORIA
# =========================
elif st.session_state.tela == "cad_monitoria":
    st.subheader("Cadastrar monitoria")

    with st.form("form_monitoria"):
        data_monitoria = st.date_input("Data", value=date.today(), key="data_monitoria")

        turma = st.selectbox(
            "Turma",
            TURMAS,
            index=None,
            placeholder="Selecione a turma",
            key="turma_monitoria",
        )

        monitor = st.selectbox(
            "Monitor",
            MONITORES,
            index=None,
            placeholder="Selecione o monitor",
        )

        conteudo = st.text_area("Conteúdo")

        arquivo_drive = st.text_input("Nome do arquivo no Drive (se houver)")

        col1, col2 = st.columns(2)
        salvar = col1.form_submit_button("Salvar", use_container_width=True)
        voltar = col2.form_submit_button("Voltar ao menu", use_container_width=True)

    if voltar:
        st.session_state.tela = "menu"
        st.rerun()

    if salvar:
        if not turma or not monitor or not conteudo.strip():
            st.error("Preencha data, turma, monitor e conteúdo.")
        else:
            inserir_monitoria(
                data_monitoria=data_monitoria,
                turma=turma,
                monitor=monitor,
                conteudo=conteudo,
                arquivo_drive=arquivo_drive,
            )
            st.session_state.mensagem = "Monitoria cadastrada com sucesso."
            st.session_state.tela = "menu"
            st.rerun()


# =========================
# CONSULTA
# =========================
elif st.session_state.tela == "consultar":
    st.subheader("Consultar registros")

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_turma = st.selectbox(
                "Turma",
                ["Todas"] + TURMAS,
                index=0,
            )

        with col2:
            filtro_mes = st.selectbox(
                "Mês",
                list(MESES.keys()),
                index=0,
            )

        with col3:
            tipo_consulta = st.selectbox(
                "Seção",
                ["Tudo", "Atividades avaliativas", "Monitorias"],
                index=0,
            )

    st.markdown("---")

    # ATIVIDADES
    if tipo_consulta in ["Tudo", "Atividades avaliativas"]:
        st.markdown("### Atividades avaliativas")

        df_ativ = buscar_atividades()

        if not df_ativ.empty:
            if filtro_turma != "Todas":
                df_ativ = df_ativ[df_ativ["turma"] == filtro_turma]

            df_ativ = filtrar_por_mes(df_ativ, filtro_mes)

        if df_ativ.empty:
            st.info("Nenhuma atividade avaliativa encontrada com esses filtros.")
        else:
            st.dataframe(
                formatar_dataframe_atividades(df_ativ),
                use_container_width=True,
                hide_index=True,
            )

    # MONITORIAS
    if tipo_consulta in ["Tudo", "Monitorias"]:
        st.markdown("### Monitorias")

        df_mon = buscar_monitorias()

        if not df_mon.empty:
            if filtro_turma != "Todas":
                df_mon = df_mon[df_mon["turma"] == filtro_turma]

            df_mon = filtrar_por_mes(df_mon, filtro_mes)
            df_mon = df_mon.sort_values("data_obj", ascending=False)

        if df_mon.empty:
            st.info("Nenhuma monitoria encontrada com esses filtros.")
        else:
            for _, linha in df_mon.iterrows():
                st.markdown(f"**{linha['data']} — {linha['turma']}**")
                st.write(f"**Monitor:** {linha['monitor']}")
                st.write(f"**Conteúdo:** {linha['conteudo']}")

                arquivo = (linha["arquivo_drive"] or "").strip()
                if arquivo:
                    st.write(f"**Arquivo no Drive:** {arquivo}")

                st.markdown("---")

    if st.button("Voltar ao menu", use_container_width=True):
        st.session_state.tela = "menu"
        st.rerun()
