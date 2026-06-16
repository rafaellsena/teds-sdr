import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell
def _setup():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from pathlib import Path

    PARQUETS = Path(r"C:\Users\rafael.lsena\Documents\SNIDR\Projeto TEDs\Parquets")

    df_teds   = pd.read_parquet(PARQUETS / "ted_analise_completa.parquet")
    df_obras  = pd.read_parquet(PARQUETS / "obras_vinculadas_teds.parquet")
    df_ev_ano = pd.read_parquet(PARQUETS / "ted_eventos_com_ano.parquet")

    # Normalizar TEDs
    df_teds["aa_ano_plano_acao"]   = df_teds["aa_ano_plano_acao"].astype(int)
    df_teds["vl_total_plano_acao"] = pd.to_numeric(df_teds["vl_total_plano_acao"], errors="coerce").fillna(0)
    df_teds["vl_total_empenhado"]  = pd.to_numeric(df_teds["vl_total_empenhado"],  errors="coerce").fillna(0)

    def abreviar(nome):
        if pd.isna(nome): return "Outros"
        nome = str(nome)
        nome = nome.replace("Companhia de Desenvolvimento dos Vales do São Francisco e do Parnaíba", "CODEVASF")
        nome = nome.replace("COMPANHIA DE DESENVOLVIMENTO DOS VALES DO SAO FRANCISCO E DO PARNAIBA", "CODEVASF")
        nome = nome.replace("Departamento Nacional de Obras Contra as Secas", "DNOCS")
        nome = nome.replace("DEPARTAMENTO NACIONAL DE OBRAS CONTRA AS SECAS", "DNOCS")
        nome = nome.replace("Superintendência do Desenvolvimento do Centro-Oeste", "SUDECO")
        nome = nome.replace("SUPERINT. DE DESENVOLVIMENTO DO CENTRO-OESTE", "SUDECO")
        nome = nome.replace("Instituto Federal de Educação, Ciência e Tecnologia", "IF")
        nome = nome.replace("Fundação Universidade Federal", "Univ. Fed.")
        nome = nome.replace("Universidade Federal", "Univ. Fed.")
        return nome.strip()

    df_teds["executor_curto"] = df_teds["unidade_descentralizada"].apply(abreviar)

    # Obras confirmadas SDR
    if "acao_governo" in df_obras.columns:
        df_obras_sdr = df_obras[df_obras["acao_governo"] == "00SX"].copy()
    else:
        df_obras_sdr = df_obras.copy()

    if "nr_empenho" in df_obras_sdr.columns:
        df_obras_sdr["ano_empenho"] = df_obras_sdr["nr_empenho"].astype(str).str[:4]
    else:
        df_obras_sdr["ano_empenho"] = "N/D"

    # Categoria do objeto dos TEDs por regex
    import re
    CATS = {
        "Pavimentação":              r"paviment|asfalto|rodovia|estrada vicinal",
        "Infraestrutura Hídrica":    r"po[çc]o|tubular|perfura|captação|cisterna|abastecimento",
        "Máquinas e Equipamentos":   r"máquina|equipamento|trator|retroescavadeira|implemento",
        "Obras de Edificação":       r"construção|reforma|ampliação|mercado|abatedouro|galpão|armazém",
        "Drenagem/Esgoto":           r"drenagem|esgoto|saneamento",
        "Irrigação":                 r"irrigação|perímetro|canal|barragem",
        "Capacitação/Pesquisa":      r"capacita|pesquisa|estudo|diagnóstico|curso",
        "Reserva Técnica":           r"reserva técnica|despesa administrativa",
    }
    def categorizar_objeto(texto):
        if pd.isna(texto): return "Outros"
        for cat, padrao in CATS.items():
            if re.search(padrao, str(texto), re.IGNORECASE):
                return cat
        return "Outros"

    df_teds["categoria_objeto"] = df_teds["tx_objeto_plano_acao"].apply(categorizar_objeto)

    print(f"TEDs: {len(df_teds)} | Obras SDR: {len(df_obras_sdr)} | Eventos: {len(df_ev_ano)}")
    return df_ev_ano, df_obras_sdr, df_teds, mo, pd, px


@app.cell
def _cabecalho(mo):
    mo.vstack([
        mo.Html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    * { font-family: 'Roboto', Arial, sans-serif !important; }
    body, .marimo { background-color: #E8E8E8 !important; }
    .dash-header {
    background:#FFFFFF;border-radius:8px;padding:24px 28px;
    margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,0.10);
    }
    .dash-header h1 { font-size:32px;font-weight:700;margin:0 0 6px 0;color:#1565c0; }
    .dash-header p  { font-size:17px;color:#666666;margin:0;font-weight:400; }
    .section-header {
    background:#1565c0;border-radius:8px;padding:14px 22px;margin:28px 0 16px 0;
    }
    .section-header h2 { font-size:20px;font-weight:700;color:#FFFFFF;margin:0; }
    .section-header p  { font-size:13px;color:#B3D4F5;margin:4px 0 0 0; }
    .subsection { font-size:15px;font-weight:600;color:#1565c0;margin:20px 0 8px 0; }
    .totais-box {
    display:flex;gap:40px;background:#FFFFFF;border-radius:8px;
    padding:18px 24px;margin-bottom:16px;
    box-shadow:0 2px 8px rgba(0,0,0,0.10);flex-wrap:wrap;
    }
    .totais-item { display:flex;flex-direction:column;gap:4px; }
    .totais-label { font-size:12px;font-weight:500;text-transform:uppercase;color:#888;letter-spacing:0.05em; }
    .totais-value { font-size:26px;font-weight:700;color:#1565c0; }
    .totais-value.verde { color:#009C3B; }
    .nota-box {
    background:#fff8f0;border-radius:8px;padding:14px 18px;
    border-left:4px solid #e65100;margin:16px 0;
    font-size:13px;color:#555;line-height:1.6;
    }
    .marimo-footer,[data-testid="marimo-footer"],
    a[href*="marimo"],div[class*="footer"] a,.made-with-marimo { display:none !important; }
    </style>
        """),
        mo.Html("""
    <div class="dash-header">
      <h1>Termos de Execução Descentralizada — SDR/MIDR</h1>
      <p>Secretaria Nacional de Políticas de Desenvolvimento Regional e Territorial &nbsp;·&nbsp; Período: 2021–2026 &nbsp;·&nbsp; Fonte: Transferegov.br · Tesouro Gerencial · Obrasgov/CIPI</p>
    </div>
        """),
    ])
    return


@app.cell
def _filtros(df_teds, mo):
    anos      = sorted(df_teds["aa_ano_plano_acao"].unique())
    ufs       = sorted(df_teds["uf_objeto"].dropna().unique())
    execs     = sorted(df_teds["executor_curto"].dropna().unique())
    situacoes = sorted(df_teds["tx_situacao_termo"].dropna().unique())

    sel_ano  = mo.ui.multiselect(options=[str(a) for a in anos], value=[str(a) for a in anos], label="Ano")
    sel_uf   = mo.ui.multiselect(options=ufs, value=ufs, label="UF")
    sel_exec = mo.ui.multiselect(options=execs, value=execs, label="Executor")
    sel_sit  = mo.ui.multiselect(options=situacoes, value=situacoes, label="Situação do Termo")

    mo.Html(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;background:#FFFFFF;border-radius:8px;
            padding:16px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.10);margin-bottom:8px;">
      <div style="flex:1;min-width:140px;">{mo.as_html(sel_ano)}</div>
      <div style="flex:1;min-width:140px;">{mo.as_html(sel_uf)}</div>
      <div style="flex:2;min-width:200px;">{mo.as_html(sel_exec)}</div>
      <div style="flex:2;min-width:200px;">{mo.as_html(sel_sit)}</div>
    </div>""")
    return sel_ano, sel_exec, sel_sit, sel_uf


@app.cell
def _filtrado(df_teds, sel_ano, sel_exec, sel_sit, sel_uf):
    df_f = df_teds[
        (df_teds["aa_ano_plano_acao"].isin([int(a) for a in sel_ano.value])) &
        (df_teds["uf_objeto"].isin(sel_uf.value) | df_teds["uf_objeto"].isna()) &
        (df_teds["executor_curto"].isin(sel_exec.value)) &
        (df_teds["tx_situacao_termo"].isin(sel_sit.value) | df_teds["tx_situacao_termo"].isna())
    ].copy()
    return (df_f,)


@app.cell
def _s1(df_ev_ano, df_f, mo, pd, px):
    vl_plan  = df_f["vl_total_plano_acao"].sum()
    vl_emp   = df_f["vl_total_empenhado"].sum()
    qt_plan  = len(df_f)
    qt_termo = df_f["tx_situacao_termo"].notna().sum()

    # ── Gráficos ─────────────────────────────────────────────────
    def layout_base(fig, h=400, l=60, r=30):
        fig.update_layout(
            font_family="Roboto", title_font_size=15, title_font_color="#1565c0",
            plot_bgcolor="white", height=h, autosize=True,
            legend=dict(orientation="h", y=-0.12, x=0, title_text=""),
            margin=dict(t=50, b=50, l=l, r=r),
        )
        return fig

    # Por UF
    _uf = (
        df_f[df_f["uf_objeto"].notna()]
        .groupby("uf_objeto")
        .agg(Planejado=("vl_total_plano_acao","sum"), Empenhado=("vl_total_empenhado","sum"))
        .reset_index().rename(columns={"uf_objeto":"UF"}).sort_values("Planejado", ascending=True)
    )
    _uf["Planejado (R$ mi)"] = (_uf["Planejado"]/1e6).round(1)
    _uf["Empenhado (R$ mi)"] = (_uf["Empenhado"]/1e6).round(1)
    _fig_uf = layout_base(px.bar(_uf, y="UF", x=["Planejado (R$ mi)","Empenhado (R$ mi)"],
        orientation="h", barmode="group", title="Valor por UF (R$ Milhões)",
        color_discrete_map={"Planejado (R$ mi)":"#1565c0","Empenhado (R$ mi)":"#009C3B"},
        template="plotly_white"), h=520, l=55)
    _fig_uf.update_layout(xaxis_title="R$ Milhões", yaxis_title="")

    # Por ano
    _ano = (
        df_f.groupby("aa_ano_plano_acao")
        .agg(Planejado=("vl_total_plano_acao","sum"), Empenhado=("vl_total_empenhado","sum"))
        .reset_index().rename(columns={"aa_ano_plano_acao":"Ano"})
    )
    _ano["Planejado (R$ mi)"] = (_ano["Planejado"]/1e6).round(1)
    _ano["Empenhado (R$ mi)"] = (_ano["Empenhado"]/1e6).round(1)
    _ano["Ano"] = _ano["Ano"].astype(str)
    _fig_ano = layout_base(px.bar(_ano, x="Ano", y=["Planejado (R$ mi)","Empenhado (R$ mi)"],
        barmode="group", title="Valor por Ano (R$ Milhões)",
        color_discrete_map={"Planejado (R$ mi)":"#1565c0","Empenhado (R$ mi)":"#009C3B"},
        template="plotly_white"), h=360)
    _fig_ano.update_layout(yaxis_title="R$ Milhões")

    # Por executor
    _exec = (
        df_f.groupby("executor_curto")
        .agg(Planejado=("vl_total_plano_acao","sum"), Empenhado=("vl_total_empenhado","sum"))
        .reset_index().rename(columns={"executor_curto":"Executor"})
        .sort_values("Planejado", ascending=True).tail(15)
    )
    _exec["Planejado (R$ mi)"] = (_exec["Planejado"]/1e6).round(1)
    _exec["Empenhado (R$ mi)"] = (_exec["Empenhado"]/1e6).round(1)
    _fig_exec = layout_base(px.bar(_exec, y="Executor", x=["Planejado (R$ mi)","Empenhado (R$ mi)"],
        orientation="h", barmode="group", title="Valor por Executor (R$ Milhões)",
        color_discrete_map={"Planejado (R$ mi)":"#1565c0","Empenhado (R$ mi)":"#009C3B"},
        template="plotly_white"), h=460, l=200)
    _fig_exec.update_layout(xaxis_title="R$ Milhões", yaxis_title="")

    # ── Tabela agrupada por ano + natureza de despesa ─────────────
    anos_selecionados = df_f["aa_ano_plano_acao"].unique()
    _ev_filtrado = df_ev_ano[df_ev_ano["aa_ano_plano_acao"].isin(anos_selecionados)].copy()

    _tab_nat = (
        _ev_filtrado.groupby(["aa_ano_plano_acao","natureza_norm"])["vl_evento"]
        .sum().reset_index()
        .rename(columns={"aa_ano_plano_acao":"Ano","natureza_norm":"Natureza de Despesa","vl_evento":"Valor"})
        .sort_values(["Ano","Valor"], ascending=[True,False])
    )
    _tab_nat["Valor (R$ mi)"] = (_tab_nat["Valor"]/1e6).round(1)
    _tab_nat["Ano"] = _tab_nat["Ano"].astype(str)
    _tab_nat_exib = _tab_nat[["Ano","Natureza de Despesa","Valor (R$ mi)"]].copy()
    _total_nat = pd.DataFrame({
        "Ano": ["TOTAL"],
        "Natureza de Despesa": [""],
        "Valor (R$ mi)": [_tab_nat_exib["Valor (R$ mi)"].sum().round(1)],
    })
    _tab_nat_exib = pd.concat([_tab_nat_exib, _total_nat], ignore_index=True)

    # ── Tabela agrupada por ano + categoria do objeto ─────────────
    _tab_cat = (
        df_f.groupby(["aa_ano_plano_acao","categoria_objeto"])
        .agg(Qt_Planos=("id_plano_acao","count"), Planejado=("vl_total_plano_acao","sum"))
        .reset_index()
        .rename(columns={"aa_ano_plano_acao":"Ano","categoria_objeto":"Categoria"})
        .sort_values(["Ano","Planejado"], ascending=[True,False])
    )
    _tab_cat["Planejado (R$ mi)"] = (_tab_cat["Planejado"]/1e6).round(1)
    _tab_cat["Ano"] = _tab_cat["Ano"].astype(str)
    _tab_cat_exib = _tab_cat[["Ano","Categoria","Qt_Planos","Planejado (R$ mi)"]].copy()
    _total_cat = pd.DataFrame({
        "Ano": ["TOTAL"],
        "Categoria": [""],
        "Qt_Planos": [_tab_cat_exib["Qt_Planos"].sum()],
        "Planejado (R$ mi)": [_tab_cat_exib["Planejado (R$ mi)"].sum().round(1)],
    })
    _tab_cat_exib = pd.concat([_tab_cat_exib, _total_cat], ignore_index=True)

    # ── Tabela detalhada dos planos ───────────────────────────────
    _cols = {
        "aa_ano_plano_acao":"Ano","tx_numero_ns_termo":"Nº TED",
        "executor_curto":"Executor","uf_objeto":"UF",
        "tx_situacao_termo":"Situação","categoria_objeto":"Categoria",
        "vl_total_plano_acao":"Valor Planejado","vl_total_empenhado":"Valor Empenhado",
        "tx_objeto_plano_acao":"Objeto",
    }
    _tab_det = df_f[[c for c in _cols if c in df_f.columns]].copy().rename(columns=_cols)
    for _c in ["Valor Planejado","Valor Empenhado"]:
        if _c in _tab_det.columns:
            _tab_det[_c] = _tab_det[_c].apply(
                lambda x: f"R$ {x/1e6:.1f} mi" if pd.notna(x) and x > 0 else "-")
    if "Objeto" in _tab_det.columns:
        _tab_det["Objeto"] = _tab_det["Objeto"].astype(str).str[:80] + "..."

    mo.vstack([
        mo.Html("""
    <div class="section-header">
      <h2>Seção 1 — Fluxo Financeiro dos TEDs</h2>
      <p>Recursos descentralizados pela SDR/MIDR · Fonte: API Transferegov.br e Tesouro Gerencial/SIAFI</p>
    </div>"""),
        mo.Html(f"""
    <div class="totais-box">
      <div class="totais-item">
    <span class="totais-label">Planos de Ação</span>
    <span class="totais-value">{qt_plan}</span>
      </div>
      <div class="totais-item">
    <span class="totais-label">Termos Assinados</span>
    <span class="totais-value">{qt_termo}</span>
      </div>
      <div class="totais-item">
    <span class="totais-label">Valor Planejado</span>
    <span class="totais-value">R$ {vl_plan/1e9:.2f} Bi</span>
      </div>
      <div class="totais-item">
    <span class="totais-label">Valor Empenhado</span>
    <span class="totais-value verde">R$ {vl_emp/1e9:.2f} Bi</span>
      </div>
    </div>"""),
        mo.Html(f"""
    <div style="display:flex;width:100%;gap:16px;">
      <div style="flex:1;min-width:0;">{mo.as_html(mo.ui.plotly(_fig_uf))}</div>
      <div style="flex:1;min-width:0;">
    {mo.as_html(mo.ui.plotly(_fig_ano))}
    {mo.as_html(mo.ui.plotly(_fig_exec))}
      </div>
    </div>"""),
        mo.Html('<div class="subsection">Valor empenhado por ano e natureza de despesa (SIAFI)</div>'),
        mo.Html('<div style="font-size:12px;color:#888;margin-bottom:8px;">Fonte: Tesouro Gerencial — cadeia PTRES → NC → NE → natureza contábil</div>'),
        mo.ui.table(_tab_nat_exib),
        mo.Html('<div class="subsection">Planos de ação por ano e categoria de entrega (texto do objeto)</div>'),
        mo.Html('<div style="font-size:12px;color:#888;margin-bottom:8px;">Fonte: campo objeto dos planos de ação no Transferegov — classificação por análise de texto · cobertura estimada: 70-75%</div>'),
        mo.ui.table(_tab_cat_exib),
        mo.Html('<div class="subsection">Lista detalhada dos planos de ação</div>'),
        mo.ui.table(_tab_det),
    ])
    return


@app.cell
def _s2(df_obras_sdr, mo, pd, px):
    col_nome = next((c for c in ["nome_obra","Nome ( Apelido )","nome"] if c in df_obras_sdr.columns), df_obras_sdr.columns[0])
    col_mun  = next((c for c in ["municipio","Município"] if c in df_obras_sdr.columns), None)
    col_uf   = next((c for c in ["uf","UF","uf_principal"] if c in df_obras_sdr.columns), None)
    col_val  = next((c for c in ["valor","vl_investimento","Investimento Previsto"] if c in df_obras_sdr.columns), None)
    col_sit  = next((c for c in ["situacao_obra","Situação"] if c in df_obras_sdr.columns), None)
    col_cat  = "categoria_obra" if "categoria_obra" in df_obras_sdr.columns else None
    col_ne   = next((c for c in ["nr_empenho","ne_completa"] if c in df_obras_sdr.columns), None)
    col_dt_i = next((c for c in ["dt_inicio","Data Inicial Prevista"] if c in df_obras_sdr.columns), None)
    col_dt_f = next((c for c in ["dt_fim","Data Final Prevista"] if c in df_obras_sdr.columns), None)

    # Mapa
    if "lat" in df_obras_sdr.columns and "lon" in df_obras_sdr.columns:
        _map_df = df_obras_sdr[df_obras_sdr["lat"].notna() & df_obras_sdr["lon"].notna()].copy()
        _hover  = {c:True for c in [col_mun, col_uf, col_sit, col_cat, "ano_empenho", col_val]
                   if c and c in _map_df.columns}
        _fig_map = px.scatter_mapbox(_map_df, lat="lat", lon="lon",
            hover_name=col_nome, hover_data=_hover,
            color=col_sit if col_sit else None,
            color_discrete_map={"Em execução":"#009C3B","Concluída":"#1565c0","Cadastrada":"#FFA500"},
            zoom=4, center={"lat":-12,"lon":-45}, mapbox_style="carto-positron",
            title=f"Obras vinculadas a TEDs da SDR ({len(_map_df)} obras com localização)")
        _fig_map.update_traces(marker=dict(size=12))
        _fig_map.update_layout(font_family="Roboto", title_font_size=15, title_font_color="#1565c0",
            height=520, margin=dict(t=50,b=10,l=10,r=10),
            legend=dict(orientation="h",y=-0.05,x=0,title_text="Situação"))
        _mapa = mo.ui.plotly(_fig_map)
    else:
        _mapa = mo.Html('<div class="nota-box">Coordenadas não disponíveis.</div>')

    # Tabela agrupada por ano + categoria
    _tab_cat = (
        df_obras_sdr.groupby(["ano_empenho", col_cat] if col_cat else ["ano_empenho"])
        .agg(
            Qt_Obras=("id_obra" if "id_obra" in df_obras_sdr.columns else col_nome, "count"),
            **({col_val: (col_val, "sum")} if col_val else {})
        )
        .reset_index()
        .rename(columns={
            "ano_empenho": "Ano",
            col_cat: "Categoria",
            col_val: "Valor Total",
        })
        .sort_values(["Ano","Valor Total"] if col_val else ["Ano"], ascending=[True, False] if col_val else [True])
    )
    _total_obras = pd.DataFrame({
        "Ano": ["TOTAL"],
        **({"Categoria": [""]} if "Categoria" in _tab_cat.columns else {}),
        "Qt_Obras": [_tab_cat["Qt_Obras"].sum()],
        **({"Valor Total": [_tab_cat["Valor Total"].sum()]} if col_val and "Valor Total" in _tab_cat.columns else {}),
    })
    _tab_cat = pd.concat([_tab_cat, _total_obras], ignore_index=True)
    if col_val and "Valor Total" in _tab_cat.columns:
        _tab_cat["Valor Total"] = _tab_cat["Valor Total"].apply(
            lambda x: f"R$ {float(x)/1e6:.1f} mi" if pd.notna(x) and x > 0 else "-")

    # Tabela detalhada
    _cols_tab = {}
    for _o, _d in [
        (col_nome,"Nome da Obra"),(col_mun,"Município"),(col_uf,"UF"),
        ("ano_empenho","Ano"),(col_dt_i,"Início Previsto"),(col_dt_f,"Fim Previsto"),
        (col_sit,"Situação"),(col_cat,"Categoria"),(col_val,"Valor"),(col_ne,"Nº Empenho"),
    ]:
        if _o and _o in df_obras_sdr.columns:
            _cols_tab[_o] = _d

    _tab_det = df_obras_sdr[list(_cols_tab.keys())].copy().rename(columns=_cols_tab)
    if "Valor" in _tab_det.columns:
        _tab_det["Valor"] = _tab_det["Valor"].apply(
            lambda x: f"R$ {float(x)/1e6:.1f} mi" if pd.notna(x) and str(x) not in ["0","0.0","nan"] else "-")
    if "Nome da Obra" in _tab_det.columns:
        _tab_det["Nome da Obra"] = _tab_det["Nome da Obra"].astype(str).str[:80]
    for _c in ["Início Previsto","Fim Previsto"]:
        if _c in _tab_det.columns:
            _tab_det[_c] = pd.to_datetime(_tab_det[_c], errors="coerce").dt.strftime("%d/%m/%Y").fillna("-")

    mo.vstack([
        mo.Html("""
    <div class="section-header">
      <h2>Seção 2 — Obras Identificadas</h2>
      <p>Obras com vínculo confirmado a recursos TEDs da SDR · Fonte: Obrasgov / CIPI / Tesouro Gerencial</p>
    </div>"""),
        mo.Html(f"""
    <div class="nota-box">
      ⚠️ <strong>Nota metodológica:</strong> das 142 obras CODEVASF/DNOCS mapeadas no Obrasgov,
      <strong>{len(df_obras_sdr)} têm vínculo confirmado</strong> com recursos TEDs da SDR,
      identificadas pela ação orçamentária <strong>00SX</strong> no CIPI e cruzadas com os empenhos
      do Tesouro Gerencial. Executores como IFAP, UNIFAP e UFRA não cadastram obras no Obrasgov —
      suas entregas não aparecem aqui.
    </div>"""),
        _mapa,
        mo.Html('<div class="subsection">Obras por ano e categoria</div>'),
        mo.ui.table(_tab_cat),
        mo.Html('<div class="subsection">Lista detalhada das obras confirmadas</div>'),
        mo.ui.table(_tab_det),
    ])
    return


@app.cell
def _rodape(mo):
    mo.Html("""
    <div style="text-align:center;padding:24px;color:#9CA3AF;font-size:12px;
            border-top:1px solid #E5E7EB;margin-top:32px;">
      Painel TEDs — SDR/MIDR &nbsp;|&nbsp; Ministério da Integração e do Desenvolvimento Regional<br>
      Fonte: API Transferegov.br &nbsp;·&nbsp; Tesouro Gerencial/SIAFI &nbsp;·&nbsp; Obrasgov/CIPI &nbsp;·&nbsp; Decreto n. 11.962/2024
    </div>
    """)
    return


if __name__ == "__main__":
    app.run()
