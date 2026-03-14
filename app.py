import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Agenda Escolar",
    page_icon="📚",
    layout="wide"
)


# =========================
# BANCO DE DADOS
# =========================
DB_NAME = "agenda_escolar.db"


def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            turma TEXT NOT NULL,
            tipo_atividade TEXT NOT NULL,
            descricao TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            turma TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            observacao TEXT
        )
    """)

    conn.commit()
    conn.close()


def inserir_avaliacao(data, turma, tipo_atividade, descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO avaliacoes (data, turma, tipo_atividade, descricao)
        VALUES (?, ?, ?, ?)
    """, (data, turma, tipo_atividade, descricao))
    conn.commit()
    conn.close()


def inserir_monitoria(data, turma, conteudo, observacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO monitorias (data, turma, conteudo, observacao)
        VALUES (?, ?, ?, ?)
    """, (data, turma, conteudo, observacao))
    conn.commit()
    conn.close()


def carregar_avaliacoes():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM avaliacoes", conn)
    conn.close()
    return df


def carregar_monitorias():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM monitorias", conn)
    conn.close()
    return df


# =========================
# FUNÇÕES AUXILIARES
# =========================
def formatar_data_br(data_str):
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return data_str


def adicionar_coluna_mes(df):
    if not df.empty and "data" in df.columns:
        df["data_dt"] = pd.to_datetime(df["data"], errors="coerce")
        df["mes"] = df["data_dt"].dt.month
        df["ano"] = df["data_dt"].dt.year
    return df


def filtrar_por_mes(df, mes):
    if df.empty:
        return df
    if mes == "Todos":
        return df
    return df[df["mes"] == int(mes)]


def filtrar_por_turma(df, turma):
    if df.empty:
        return df
    if turma == "Todas":
        return df
    return df[df["turma"] == turma]


# =========================
# INICIALIZAÇÃO
# =========================
criar_tabelas()

st.title("📚 Agenda Escolar")
st.caption("Cadastro e consulta de avaliações e monitorias")


# =========================
# ABAS PRINCIPAIS
# =========================
aba1, aba2, aba3 = st.tabs(["Cadastrar Avaliação", "Cadastrar Monitoria", "Consultar"])


# =========================
# ABA 1 - CADASTRAR AVALIAÇÃO
# =========================
with aba1:
    st.subheader("Cadastrar atividade avaliativa")

    with st.form("form_avaliacao"):
        col1, col2 = st.columns(2)

        with col1:
            data_av = st.date_input("Data")
            turma_av = st.text_input("Turma", placeholder="Ex.: 7º Ano A")

        with col2:
            tipo_av = st.selectbox(
                "Tipo de atividade",
                ["Prova", "Trabalho", "Lista de exercícios", "Seminário", "Outro"]
            )
            descricao_av = st.text_input("Descrição", placeholder="Ex.: Capítulos 3 e 4")

        enviar_av = st.form_submit_button("Salvar avaliação")

        if enviar_av:
            if turma_av.strip() == "":
                st.error("Preencha a turma.")
            else:
                inserir_avaliacao(
                    data_av.strftime("%Y-%m-%d"),
                    turma_av.strip(),
                    tipo_av.strip(),
                    descricao_av.strip()
                )
                st.success("Avaliação cadastrada com sucesso.")


# =========================
# ABA 2 - CADASTRAR MONITORIA
# =========================
with aba2:
    st.subheader("Cadastrar monitoria")

    with st.form("form_monitoria"):
        col1, col2 = st.columns(2)

        with col1:
            data_mon = st.date_input("Data", key="data_monitoria")
            turma_mon = st.text_input("Turma", placeholder="Ex.: 8º Ano B", key="turma_monitoria")

        with col2:
            conteudo_mon = st.text_area("Conteúdo", placeholder="Ex.: Revisão de frações")
            observacao_mon = st.text_area("Observação", placeholder="Ex.: Turma participou bem")

        enviar_mon = st.form_submit_button("Salvar monitoria")

        if enviar_mon:
            if turma_mon.strip() == "" or conteudo_mon.strip() == "":
                st.error("Preencha pelo menos a turma e o conteúdo.")
            else:
                inserir_monitoria(
                    data_mon.strftime("%Y-%m-%d"),
                    turma_mon.strip(),
                    conteudo_mon.strip(),
                    observacao_mon.strip()
                )
                st.success("Monitoria cadastrada com sucesso.")


# =========================
# ABA 3 - CONSULTAR
# =========================
with aba3:
    st.subheader("Consultar registros")

    df_av = carregar_avaliacoes()
    df_mon = carregar_monitorias()

    df_av = adicionar_coluna_mes(df_av)
    df_mon = adicionar_coluna_mes(df_mon)

    turmas_av = sorted(df_av["turma"].dropna().unique().tolist()) if not df_av.empty else []
    turmas_mon = sorted(df_mon["turma"].dropna().unique().tolist()) if not df_mon.empty else []
    turmas_unicas = sorted(list(set(turmas_av + turmas_mon)))

    colf1, colf2 = st.columns(2)

    with colf1:
        mes_escolhido = st.selectbox(
            "Filtrar por mês",
            ["Todos", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            format_func=lambda x: (
                "Todos" if x == "Todos" else
                {
                    1: "Janeiro",
                    2: "Fevereiro",
                    3: "Março",
                    4: "Abril",
                    5: "Maio",
                    6: "Junho",
                    7: "Julho",
                    8: "Agosto",
                    9: "Setembro",
                    10: "Outubro",
                    11: "Novembro",
                    12: "Dezembro"
                }[x]
            )
        )

    with colf2:
        turma_escolhida = st.selectbox(
            "Filtrar por turma",
            ["Todas"] + turmas_unicas
        )

    if st.button("Consultar"):
        # FILTRO AVALIAÇÕES
        av_filtrado = filtrar_por_mes(df_av, mes_escolhido)
        av_filtrado = filtrar_por_turma(av_filtrado, turma_escolhida)

        # FILTRO MONITORIAS
        mon_filtrado = filtrar_por_mes(df_mon, mes_escolhido)
        mon_filtrado = filtrar_por_turma(mon_filtrado, turma_escolhida)

        st.markdown("---")
        st.subheader("Atividades avaliativas")

        if av_filtrado.empty:
            st.info("Nenhuma atividade avaliativa encontrada.")
        else:
            av_filtrado = av_filtrado.sort_values(by="data_dt", ascending=True)

            tabela_av = av_filtrado[["data", "tipo_atividade", "turma"]].copy()
            tabela_av["data"] = tabela_av["data"].apply(formatar_data_br)
            tabela_av.columns = ["Data", "Tipo de atividade", "Turma"]

            st.dataframe(tabela_av, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Monitorias")

        if mon_filtrado.empty:
            st.info("Nenhuma monitoria encontrada.")
        else:
            mon_filtrado = mon_filtrado.sort_values(by="data_dt", ascending=False)

            for _, linha in mon_filtrado.iterrows():
                data_br = formatar_data_br(linha["data"])
                turma = linha["turma"]
                conteudo = linha["conteudo"]
                observacao = linha["observacao"] if pd.notna(linha["observacao"]) else ""

                st.markdown(
                    f"""
                    **Dia:** {data_br}  
                    **Turma:** {turma}  
                    **Conteúdo:** {conteudo}  
                    **Observação:** {observacao if observacao.strip() else "-"}
                    """
                )
                st.markdown("---")
