import os
from datetime import datetime

import pandas as pd
import streamlit as st

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="SisteMat",
    page_icon="📘",
    layout="wide"
)

st.title("📘 SisteMat")
st.caption("Sistema de registro e consulta de avaliações, atividades e monitorias")

# =========================
# ARQUIVOS DE DADOS
# =========================
ARQ_AVALIACOES = "avaliacoes.csv"
ARQ_MONITORIA = "monitoria.csv"

# =========================
# LISTAS FIXAS
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
    "Atividade avaliativa",
    "Teste",
    "Prova",
    "Trabalho",
    "Simulado",
    "Lista",
    "Outro",
]

MONITORES = [
    "Luiza",
    "Rafael",
    "Arthur",
    "Gabriel",
]

MESES = {
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

# =========================
# FUNÇÕES AUXILIARES
# =========================
def inicializar_arquivos():
    if not os.path.exists(ARQ_AVALIACOES):
        df = pd.DataFrame(columns=["data", "turma", "tipo", "descricao", "monitor"])
        df.to_csv(ARQ_AVALIACOES, index=False, encoding="utf-8-sig")

    if not os.path.exists(ARQ_MONITORIA):
        df = pd.DataFrame(columns=["data", "turma", "conteudo", "arquivo_drive", "monitor"])
        df.to_csv(ARQ_MONITORIA, index=False, encoding="utf-8-sig")


def carregar_csv(caminho):
    try:
        return pd.read_csv(caminho, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame()


def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False, encoding="utf-8-sig")


def formatar_data_br(data_str):
    try:
        return pd.to_datetime(data_str).strftime("%d/%m/%Y")
    except Exception:
        return data_str


def extrair_ano_ordem(turma):
    ordem = {
        "6º ano A": 1,
        "6º ano B": 2,
        "7º ano": 3,
        "8º ano": 4,
        "9º ano": 5,
        "1ª série EM": 6,
        "2ª série EM": 7,
    }
    return ordem.get(turma, 999)


def preparar_df_avaliacoes(df):
    if df.empty:
        return df
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["mes"] = df["data"].dt.month
    df["ordem_turma"] = df["turma"].apply(extrair_ano_ordem)
    return df


def preparar_df_monitoria(df):
    if df.empty:
        return df
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["mes"] = df["data"].dt.month
    df["ordem_turma"] = df["turma"].apply(extrair_ano_ordem)
    return df


def voltar_menu():
    st.session_state["tela"] = "menu"
    st.rerun()


# =========================
# INICIALIZAÇÃO
# =========================
inicializar_arquivos()

if "tela" not in st.session_state:
    st.session_state["tela"] = "menu"

# =========================
# MENU PRINCIPAL
# =========================
if st.session_state["tela"] == "menu":
    st.subheader("Menu principal")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Cadastrar avaliação/atividade", use_container_width=True):
            st.session_state["tela"] = "cad_avaliacao"
            st.rerun()

    with col2:
        if st.button("👩‍🏫 Cadastrar monitoria", use_container_width=True):
            st.session_state["tela"] = "cad_monitoria"
            st.rerun()

    with col3:
        if st.button("🔎 Consultar registros", use_container_width=True):
            st.session_state["tela"] = "consulta"
            st.rerun()

# =========================
# CADASTRO DE AVALIAÇÃO
# =========================
elif st.session_state["tela"] == "cad_avaliacao":
    st.subheader("Cadastrar avaliação / atividade avaliativa")

    with st.form("form_avaliacao", clear_on_submit=True):
        data = st.date_input("Data", format="DD/MM/YYYY")
        turma = st.selectbox("Turma", TURMAS)
        tipo = st.selectbox("Tipo de avaliação", TIPOS_AVALIACAO)
        descricao = st.text_area("Descrição / conteúdo")
        monitor = st.selectbox("Monitor", MONITORES)

        col1, col2 = st.columns(2)
        salvar = col1.form_submit_button("Salvar", use_container_width=True)
        cancelar = col2.form_submit_button("Voltar ao menu", use_container_width=True)

    if salvar:
        df = carregar_csv(ARQ_AVALIACOES)
        novo = pd.DataFrame([{
            "data": pd.to_datetime(data).strftime("%Y-%m-%d"),
            "turma": turma,
            "tipo": tipo,
            "descricao": descricao,
            "monitor": monitor,
        }])
        df = pd.concat([df, novo], ignore_index=True)
        salvar_csv(df, ARQ_AVALIACOES)
        st.success("Registro salvo com sucesso.")
        voltar_menu()

    if cancelar:
        voltar_menu()

# =========================
# CADASTRO DE MONITORIA
# =========================
elif st.session_state["tela"] == "cad_monitoria":
    st.subheader("Cadastrar monitoria")

    with st.form("form_monitoria", clear_on_submit=True):
        data = st.date_input("Data", format="DD/MM/YYYY")
        turma = st.selectbox("Turma", TURMAS)
        conteudo = st.text_area("Conteúdo")
        arquivo_drive = st.text_input("Nome do arquivo no Drive (se houver)")
        monitor = st.selectbox("Monitor", MONITORES)

        col1, col2 = st.columns(2)
        salvar = col1.form_submit_button("Salvar", use_container_width=True)
        cancelar = col2.form_submit_button("Voltar ao menu", use_container_width=True)

    if salvar:
        df = carregar_csv(ARQ_MONITORIA)
        novo = pd.DataFrame([{
            "data": pd.to_datetime(data).strftime("%Y-%m-%d"),
            "turma": turma,
            "conteudo": conteudo,
            "arquivo_drive": arquivo_drive,
            "monitor": monitor,
        }])
        df = pd.concat([df, novo], ignore_index=True)
        salvar_csv(df, ARQ_MONITORIA)
        st.success("Monitoria salva com sucesso.")
        voltar_menu()

    if cancelar:
        voltar_menu()

# =========================
# CONSULTA
# =========================
elif st.session_state["tela"] == "consulta":
    st.subheader("Consulta de registros")

    df_av = preparar_df_avaliacoes(carregar_csv(ARQ_AVALIACOES))
    df_mo = preparar_df_monitoria(carregar_csv(ARQ_MONITORIA))

    st.markdown("### Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tipo_registro = st.selectbox(
            "Tipo de registro",
            ["Avaliações/Atividades", "Monitorias"]
        )

    with col2:
        turma_filtro = st.selectbox("Turma", ["Todas"] + TURMAS)

    with col3:
        mes_filtro = st.selectbox("Mês", ["Todos"] + list(MESES.keys()))

    with col4:
        monitor_filtro = st.selectbox("Monitor", ["Todos"] + MONITORES)

    if tipo_registro == "Avaliações/Atividades":
        if df_av.empty:
            st.info("Nenhum registro de avaliação/atividade encontrado.")
        else:
            df_filtrado = df_av.copy()

            if turma_filtro != "Todas":
                df_filtrado = df_filtrado[df_filtrado["turma"] == turma_filtro]

            if mes_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["mes"] == MESES[mes_filtro]]

            if monitor_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["monitor"] == monitor_filtro]

            tipo_filtro = st.selectbox("Tipo de avaliação", ["Todos"] + TIPOS_AVALIACAO)

            if tipo_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["tipo"] == tipo_filtro]

            df_filtrado = df_filtrado.sort_values(
                by=["data", "ordem_turma"],
                ascending=[False, True]
            )

            if df_filtrado.empty:
                st.warning("Nenhum resultado encontrado com esses filtros.")
            else:
                exibir = df_filtrado.copy()
                exibir["data"] = exibir["data"].dt.strftime("%d/%m/%Y")
                exibir = exibir[["data", "tipo", "turma", "descricao", "monitor"]]
                exibir.columns = ["Data", "Tipo de atividade", "Turma", "Descrição", "Monitor"]
                st.dataframe(exibir, use_container_width=True, hide_index=True)

    else:
        if df_mo.empty:
            st.info("Nenhum registro de monitoria encontrado.")
        else:
            df_filtrado = df_mo.copy()

            if turma_filtro != "Todas":
                df_filtrado = df_filtrado[df_filtrado["turma"] == turma_filtro]

            if mes_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["mes"] == MESES[mes_filtro]]

            if monitor_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["monitor"] == monitor_filtro]

            df_filtrado = df_filtrado.sort_values(
                by=["data", "ordem_turma"],
                ascending=[False, True]
            )

            if df_filtrado.empty:
                st.warning("Nenhum resultado encontrado com esses filtros.")
            else:
                for _, row in df_filtrado.iterrows():
                    data_formatada = row["data"].strftime("%d/%m/%Y") if pd.notnull(row["data"]) else ""
                    st.markdown(
                        f"""
                        ---
                        **Data:** {data_formatada}  
                        **Turma:** {row['turma']}  
                        **Monitor:** {row['monitor']}  
                        **Conteúdo:** {row['conteudo']}  
                        **Nome do arquivo no Drive:** {row['arquivo_drive'] if pd.notnull(row['arquivo_drive']) and str(row['arquivo_drive']).strip() else "—"}
                        """
                    )

    st.markdown("---")
    if st.button("⬅️ Voltar ao menu principal"):
        voltar_menu()
