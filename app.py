import sqlite3 from datetime import date

import pandas as pd import streamlit as st

=========================

CONFIGURAÇÃO DA PÁGINA

=========================

st.set_page_config(page_title="Agenda Escolar", page_icon="📘", layout="wide")

=========================

LISTAS FIXAS

=========================

TURMAS = [ "Sexto A", "Sexto B", "Sétimo", "Oitavo", "Nono", "Primeira série do ensino médio", "Segunda série do ensino médio", ]

TIPOS_ATIVIDADE = [ "Avaliação mensal", "Testinho", "Avaliação trimestral", "Avaliação suplementar", ]

PROFESSORES = [ "Luísa", "Arthur", "Rafael", "Gabriel", ]

MESES = { "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12, }

=========================

BANCO DE DADOS

=========================

DB_NAME = "agenda_escolar.db"

def get_connection(): return sqlite3.connect(DB_NAME, check_same_thread=False)

conn = get_connection()

def criar_tabelas(): cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS atividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        turma TEXT NOT NULL,
        tipo TEXT NOT NULL
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS monitorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        turma TEXT NOT NULL,
        professor TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        observacoes TEXT
    )
    """
)

conn.commit()

criar_tabelas()

=========================

FUNÇÕES AUXILIARES

=========================

def inserir_atividade(data_registro, turma, tipo): cursor = conn.cursor() cursor.execute( "INSERT INTO atividades (data, turma, tipo) VALUES (?, ?, ?)", (data_registro.isoformat(), turma, tipo), ) conn.commit()

def inserir_monitoria(data_registro, turma, professor, conteudo, observacoes): cursor = conn.cursor() cursor.execute( """ INSERT INTO monitorias (data, turma, professor, conteudo, observacoes) VALUES (?, ?, ?, ?, ?) """, (data_registro.isoformat(), turma, professor, conteudo, observacoes), ) conn.commit()

def consultar_atividades(turmas=None, meses=None): query = "SELECT data, tipo, turma FROM atividades WHERE 1=1" params = []

if turmas:
    placeholders = ",".join(["?"] * len(turmas))
    query += f" AND turma IN ({placeholders})"
    params.extend(turmas)

if meses:
    placeholders = ",".join(["?"] * len(meses))
    query += f" AND CAST(strftime('%m', data) AS INTEGER) IN ({placeholders})"
    params.extend(meses)

query += " ORDER BY data DESC"

return pd.read_sql_query(query, conn, params=params)

def consultar_monitorias(turmas=None, professores=None, meses=None): query = """ SELECT data, turma, professor, conteudo, observacoes FROM monitorias WHERE 1=1 """ params = []

if turmas:
    placeholders = ",".join(["?"] * len(turmas))
    query += f" AND turma IN ({placeholders})"
    params.extend(turmas)

if professores:
    placeholders = ",".join(["?"] * len(professores))
    query += f" AND professor IN ({placeholders})"
    params.extend(professores)

if meses:
    placeholders = ",".join(["?"] * len(meses))
    query += f" AND CAST(strftime('%m', data) AS INTEGER) IN ({placeholders})"
    params.extend(meses)

query += " ORDER BY data DESC"

return pd.read_sql_query(query, conn, params=params)

def formatar_data_br(data_iso): try: return pd.to_datetime(data_iso).strftime("%d/%m/%Y") except Exception: return data_iso

def exibir_bloco_monitoria(linha): st.markdown( f""" <div style="
border: 1px solid #d9d9d9;
border-radius: 12px;
padding: 16px;
margin-bottom: 14px;
background-color: #fafafa;
"> <p><strong>Turma:</strong> {linha['turma']}</p> <p><strong>Data:</strong> {formatar_data_br(linha['data'])}</p> <p><strong>Professor:</strong> {linha['professor']}</p> <p><strong>Conteúdo:</strong> {linha['conteudo']}</p> <p><strong>Observações:</strong> {linha['observacoes'] if linha['observacoes'] else '-'}</p> </div> """, unsafe_allow_html=True, )

=========================

SIDEBAR / NAVEGAÇÃO

=========================

st.sidebar.title("📘 Agenda Escolar") selecao = st.sidebar.radio( "Escolha uma área:", [ "Cadastrar atividade avaliativa", "Consultar atividades", "Registrar monitoria", "Consultar monitorias", ], )

=========================

TELA: CADASTRAR ATIVIDADE

=========================

if selecao == "Cadastrar atividade avaliativa": st.title("Cadastrar atividade avaliativa")

with st.form("form_atividade", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        data_atividade = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
    with col2:
        turma_atividade = st.selectbox("Turma", TURMAS)
    with col3:
        tipo_atividade = st.selectbox("Tipo de atividade", TIPOS_ATIVIDADE)

    salvar_atividade = st.form_submit_button("Salvar")

    if salvar_atividade:
        inserir_atividade(data_atividade, turma_atividade, tipo_atividade)
        st.success("Atividade avaliativa cadastrada com sucesso.")

=========================

TELA: CONSULTAR ATIVIDADES

=========================

elif selecao == "Consultar atividades": st.title("Consultar atividades")

col1, col2 = st.columns(2)

with col1:
    turmas_filtro = st.multiselect("Filtrar por turma", TURMAS)

with col2:
    meses_escolhidos = st.multiselect("Filtrar por mês", list(MESES.keys()))

meses_numeros = [MESES[mes] for mes in meses_escolhidos]

df_atividades = consultar_atividades(turmas=turmas_filtro, meses=meses_numeros)

if df_atividades.empty:
    st.info("Nenhuma atividade encontrada para os filtros selecionados.")
else:
    df_atividades["data"] = df_atividades["data"].apply(formatar_data_br)
    df_atividades.columns = ["Data", "Tipo de atividade", "Turma"]
    st.dataframe(df_atividades, use_container_width=True, hide_index=True)

=========================

TELA: REGISTRAR MONITORIA

=========================

elif selecao == "Registrar monitoria": st.title("Registrar monitoria")

with st.form("form_monitoria", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        data_monitoria = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
    with col2:
        turma_monitoria = st.selectbox("Turma", TURMAS)
    with col3:
        professor_monitoria = st.selectbox("Professor", PROFESSORES)

    conteudo_monitoria = st.text_area("Conteúdo")
    observacoes_monitoria = st.text_area("Observações")

    salvar_monitoria = st.form_submit_button("Salvar")

    if salvar_monitoria:
        if not conteudo_monitoria.strip():
            st.error("O campo conteúdo é obrigatório.")
        else:
            inserir_monitoria(
                data_monitoria,
                turma_monitoria,
                professor_monitoria,
                conteudo_monitoria.strip(),
                observacoes_monitoria.strip(),
            )
            st.success("Monitoria registrada com sucesso.")

=========================

TELA: CONSULTAR MONITORIAS

=========================

elif selecao == "Consultar monitorias": st.title("Consultar monitorias")

col1, col2, col3 = st.columns(3)

with col1:
    turmas_filtro = st.multiselect("Filtrar por turma", TURMAS)
with col2:
    professores_filtro = st.multiselect("Filtrar por professor", PROFESSORES)
with col3:
    meses_escolhidos = st.multiselect("Filtrar por mês", list(MESES.keys()))

meses_numeros = [MESES[mes] for mes in meses_escolhidos]

df_monitorias = consultar_monitorias(
    turmas=turmas_filtro,
    professores=professores_filtro,
    meses=meses_numeros,
)

if df_monitorias.empty:
    st.info("Nenhuma monitoria encontrada para os filtros selecionados.")
else:
    for _, linha in df_monitorias.iterrows():
        exibir_bloco_monitoria(linha)
