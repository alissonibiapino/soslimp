#!/usr/bin/env python3
"""Gerador de vendas sintéticas do SOSLimp (Projeto Integrador III) - Versão Tunada (6 Anos).

Gera 72 meses (6 anos: 2020 a 2026) de vendas, movimentações e estoque final em CSV,
incluindo comportamentos reais:
  1. Pandemia (2020-2022): explosão de Álcool, Água Sanitária e Desinfetantes.
  2. Inauguração da Loja 2 há 3 anos (Nov/2023) com curva de maturação (ramp-up).
  3. Férias escolares (Jan, Jul, fim de Dez): queda de fluxo por proximidade às escolas.
  4. Feriados nacionais (queda brusca) e antecipação na véspera (+12%).
  5. Clima/Temperatura diária: dias de calor (>26°C) disparam vendas para lava-rápidos (linha automotiva).
  6. Ciclos de pagamento (início do mês forte vs. fim do mês fraco).
  7. Evolução histórica do PIX (de 5% no lançamento em 2020 até 40% em 2026).
  8. Surto de Dengue (Verão/Outono de 2024): pico em Água Sanitária e Desinfetantes.
  9. Choques semanais independentes: semanas variam sem carregar automaticamente
     a força da semana anterior; clima e sazonalidade continuam tendo memória.
"""
import csv
import json
import math
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

# =============================================================================
# 1. PARÂMETROS E PREMISSAS DO GERADOR
# =============================================================================
SEED = 67
DATA_INICIO = date(2020, 1, 1)          # Início fixo do histórico
DATA_FIM = date(2026, 11, 3)            # Data final fixa para reprodutibilidadeMESES = 72                              # 6 anos de histórico (Nov/2020 a Nov/2026)

# Inauguração da Loja 2 (aberta há exatos 3 anos antes de DATA_FIM)
DATA_ABERTURA_LOJA_2 = date(2023, 11, 3)
DIAS_MATURACAO_LOJA_2 = 180             # 6 meses para a Loja 2 atingir 100% do seu potencial

# Volume e ticket alvo nos últimos 12 meses (com as duas lojas maduras)
PEDIDOS_MES = 630
TICKET_ALVO = 14.00
PARTICIPACAO_LOJA = {1: 0.55, 2: 0.45}

# Dinâmica macro da demanda
TENDENCIA_ANUAL = 0.05                  # Crescimento orgânico de ~5% ao ano
CHOQUE_SEMANAL_SIGMA = 0.12             # Volatilidade semanal independente (lognormal)
RUIDO_DIARIO_FORMA = 25
INFLACAO_ANUAL = 0.045                  # Reajuste de preços todo dia 1º de janeiro

# Sazonalidade mensal base (já considerando queda nas férias escolares de Jan e Jul)
FATOR_MES = {
    1: 0.82,   # Janeiro: Férias escolares (movimento fraco perto das escolas)
    2: 1.04,   # Fevereiro: Volta às aulas (escolas comprando material de limpeza)
    3: 1.02,
    4: 1.00,
    5: 0.96,
    6: 1.02,
    7: 0.88,   # Julho: Recesso escolar de inverno (queda de fluxo nas lojas)
    8: 1.04,   # Agosto: Retorno do 2º semestre escolar
    9: 0.95,
    10: 1.02,
    11: 1.12,  # Novembro: Black Friday e preparação de fim de ano
    12: 1.13,  # Dezembro: Faxina de fim de ano (1ª quinzena forte, 2ª quinzena férias)
}

FATOR_DIA_SEMANA = {0: .85, 1: .95, 2: .95, 3: 1.00, 4: 1.15, 5: 1.20, 6: .60}
BLACK_FRIDAY = (11, 20, 30, 1.20)
NATAL = (12, 10, 23, 1.18)

# Feriados Nacionais Fixos (mês, dia)
FERIADOS_FIXOS = {
    (1, 1),    # Confraternização Universal
    (4, 21),   # Tiradentes
    (5, 1),    # Dia do Trabalho
    (9, 7),    # Independência do Brasil
    (10, 12),  # Nossa Senhora Aparecida
    (11, 2),   # Finados
    (11, 15),  # Proclamação da República
    (11, 20),  # Consciência Negra
    (12, 25),  # Natal
}

# Clima: Temperatura máxima média mensal de São Paulo (°C - referência histórica INMET)
TEMP_MAX_MEDIA_MES = {
    1: 28.5, 2: 29.0, 3: 28.0, 4: 26.0, 5: 23.0, 6: 21.5,
    7: 21.5, 8: 23.5, 9: 25.0, 10: 26.5, 11: 27.0, 12: 28.0
}

# Pedidos: itens por pedido e quantidade por item
P_ITENS = [(1, .78), (2, .17), (3, .05)]
P_QTD2 = 0.07
P_RECOMENDACAO = 0.05

# Popularidade base dos produtos
POPULARIDADE = {
    "Álcool 70% 1L": 18, "Desinfetante 1L": 8, "Água Sanitária 1L": 7,
    "Detergente 500ml": 6, "Detergente 500ml alta eficiência": 4,
    "Desengordurante 400ml": 2, "Desengordurante 1L": 2,
    "Limpador Multiuso 500ml": 6, "Sabão em Pó 1kg": 5, "Amaciante 1L": 5,
    "Esponja Dupla Face": 5, "Pano Multiuso": 4, "Limpa Vidros 500ml": 4,
    "Desinfetante 2L": 4, "Sabão Líquido 1L": 3.5, "Limpador Multiuso 1L": 3.5,
    "Álcool Gel 500ml": 3, "Desinfetante 5L": 3, "Detergente 5L": 3,
    "Amaciante 2L": 3, "Água Sanitária 5L": 2.5, "Sabonete Antibacteriano": 2.5,
    "Odorizador Spray": 2.5, "Desinfetante 3L": 2.5,
}

SAZONALIDADE_PRODUTO = [
    ("Álcool", 0.20, 7), ("Amaciante", 0.15, 6), ("Sabão", 0.10, 6),
    ("Odorizador", 0.15, 12), ("Desinfetante", 0.15, 1), ("Água Sanitária", 0.15, 1),
]

# Parâmetros de Estoque
REVISAO_DIA_SEMANA = 0
PRAZO_ENTREGA = (2, 5)
COBERTURA_MINIMO_DIAS = 10
COBERTURA_REPOSICAO_DIAS = 14
MINIMO_PISO = 6

# Cenário final de teste para o frontend
N_ZERADOS = (2, 3)
PCT_CRITICO = 0.10
PCT_BAIXO = 0.15

# Cadastro de colaboradores
COLAB_LOJA = {1: [1, 2], 2: [3]}
ADMISSAO = {1: date(2000, 1, 1), 2: date(2022, 7, 4), 3: date(2024, 2, 10)}
COLAB_DONO = 1
FRAGRANCIA_PADRAO = 18

BASE = Path(__file__).resolve().parent
SQL_02 = BASE.parent / "gerar_banco" / "02_dados_iniciais.sql"
SAIDA = BASE.parent / "gerar_banco" / "dados"


# =============================================================================
# 2. LEITURA DO CADASTRO (02_dados_iniciais.sql)
# =============================================================================
def ler_cadastro():
    txt = SQL_02.read_text(encoding="utf-8")
    bloco = txt.split("INSERT INTO produto (", 1)[1].split("INSERT INTO fragrancia", 1)[0]
    linhas = re.findall(r"\((\d+), '([^']*)', '([^']*)', '([^']*)', ([\d.]+), '([^']*)'\)", bloco)
    produtos = []
    for i, (c, n, d_prod, _m, p, _u) in enumerate(linhas):
        nome_lower = (n + " " + d_prod).lower()
        # Identifica produtos automotivos / lava-rápido por categoria ou palavras-chave
        eh_auto = any(termo in nome_lower for termo in [
            "auto", "carro", "veic", "pneu", "silicone", "cera", "shampoo", "limpa vidros", "pano microfibra"
        ])
        produtos.append({
            "cod": i + 1, "cat": int(c), "nome": n, "preco": float(p), "automotivo": eh_auto
        })
    assert len(produtos) == 43, f"esperava 43 produtos, li {len(produtos)}"

    bloco = txt.split("INSERT INTO produto_fragrancia VALUES", 1)[1].split("-- SELECTS", 1)[0]
    frag = defaultdict(list)
    for p, f in re.findall(r"\((\d+), (\d+)\)", bloco):
        frag[int(p)].append(int(f))
    return produtos, frag


# =============================================================================
# 3. REGRAS DE CALENDÁRIO, CLIMA, PANDEMIA E LOJAS
# =============================================================================
def normalizar(d):
    media = sum(d.values()) / len(d)
    return {k: v / media for k, v in d.items()}


MES = normalizar(FATOR_MES)
DIA = normalizar(FATOR_DIA_SEMANA)


def gerar_serie_temperaturas(dias, rng):
    """Simula a temperatura máxima diária (°C) com memória climática de 3 dias (ondas de calor/frio)."""
    temperaturas = {}
    desvio_ontem = 0.0
    for d in dias:
        media_mes = TEMP_MAX_MEDIA_MES[d.month]
        # Onda climática: 65% do desvio do dia anterior se mantém hoje
        desvio_hoje = 0.65 * desvio_ontem + rng.normal(0, 2.2)
        temperaturas[d] = round(media_mes + desvio_hoje, 1)
        desvio_ontem = desvio_hoje
    return temperaturas


def participacao_loja_no_dia(cod_loja, d):
    """Retorna a fatia de demanda da loja no dia (considerando abertura da Loja 2 há 3 anos)."""
    if cod_loja == 1:
        return PARTICIPACAO_LOJA[1]
    
    # Loja 2: Fechada antes da inauguração
    if d < DATA_ABERTURA_LOJA_2:
        return 0.0
    
    # Curva de ramp-up nos primeiros 6 meses de vida da Loja 2 (começa em 40% e vai até 100%)
    dias_aberta = (d - DATA_ABERTURA_LOJA_2).days
    if dias_aberta < DIAS_MATURACAO_LOJA_2:
        fator_maturacao = 0.40 + 0.60 * (dias_aberta / DIAS_MATURACAO_LOJA_2)
        return PARTICIPACAO_LOJA[2] * fator_maturacao
        
    return PARTICIPACAO_LOJA[2]


def fator_dia(d):
    """Calcula o multiplicador de movimento do dia (Tendência, Férias, Salário, Feriados e Datas)."""
    anos = (d - DATA_FIM).days / 365.25
    f = (1 + TENDENCIA_ANUAL) ** anos * MES[d.month] * DIA[d.weekday()]

    # 1. Efeito Salário / 5º dia útil (início do mês forte, fim de mês fraco)
    if 1 <= d.day <= 10:
        f *= 1.12
    elif d.day >= 24 and d.month not in (11, 12):
        f *= 0.90

    # 2. Férias escolares de fim de ano (após 15 de dezembro as escolas ao redor fecham)
    if d.month == 12 and d.day >= 16:
        f *= 0.92

    # 3. Datas comerciais (Black Friday e Natal)
    for m, ini, fim, k in (BLACK_FRIDAY, NATAL):
        if d.month == m and ini <= d.day <= fim:
            f *= k

    # 4. Feriados Nacionais e Vésperas
    amanha = d + timedelta(days=1)
    if (d.month, d.day) in FERIADOS_FIXOS:
        f *= 0.15  # Feriado: queda drástica de movimento
    elif (amanha.month, amanha.day) in FERIADOS_FIXOS:
        f *= 1.12  # Véspera de feriado: clientes antecipam compras

    return f


def probabilidades_pagamento_no_dia(d):
    """Evolução histórica do PIX (lançado em Nov/2020) frente ao dinheiro e cartões."""
    # Códigos: 1 = DÉBITO, 2 = CRÉDITO, 3 = PIX, 4 = DINHEIRO
    progresso_anos = max(0.0, min(1.0, (d - date(2020, 11, 1)).days / (6 * 365.25)))
    
    p_pix = 0.05 + 0.35 * progresso_anos        # Sobe de 5% em 2020 para 40% em 2026
    p_dinheiro = 0.38 - 0.23 * progresso_anos   # Cai de 38% em 2020 para 15% em 2026
    p_debito = 0.32 - 0.07 * progresso_anos     # Ajusta de 32% para 25%
    p_credito = 1.0 - (p_pix + p_dinheiro + p_debito)
    return [1, 2, 3, 4], [p_debito, p_credito, p_pix, p_dinheiro]


def fator_preco(d):
    return (1 + INFLACAO_ANUAL) ** -(DATA_FIM.year - d.year)


def preco_em(preco_atual, d):
    return max(0.5, round(preco_atual * fator_preco(d) * 20) / 20)


def pesos_produtos_base(produtos, gama):
    """Calcula os pesos mensais base de cada produto."""
    pop = np.array([POPULARIDADE.get(p["nome"], 1.0) for p in produtos])
    preco = np.array([p["preco"] for p in produtos])
    base = pop * preco ** (-gama)
    por_mes = {}
    for m in range(1, 13):
        sz = np.ones(len(produtos))
        for i, p in enumerate(produtos):
            for chave, amp, pico in SAZONALIDADE_PRODUTO:
                if chave in p["nome"]:
                    sz[i] = 1 + amp * math.cos(2 * math.pi * (m - pico) / 12)
                    break
        w = base * sz
        por_mes[m] = w / w.sum()
    media = base / base.sum()
    return por_mes, media


def ajustar_pesos_no_dia(pesos_mes_atual, produtos, d, temp_max):
    """Ajusta as probabilidades de venda dos produtos conforme Pandemia, Calor (Lava-rápidos) e Dengue."""
    w = pesos_mes_atual.copy()

    for i, p in enumerate(produtos):
        nome = p["nome"]

        # 1. EFEITO PANDEMIA (2020 a meados de 2022)
        if d.year <= 2022:
            intensidade_pandemia = max(0.0, (date(2022, 8, 1) - d).days / 600.0)
            if "Álcool" in nome or "Antibacteriano" in nome:
                w[i] *= (1.0 + 1.60 * intensidade_pandemia)  # Até 2.6x mais venda no auge
            elif "Água Sanitária" in nome or "Desinfetante" in nome:
                w[i] *= (1.0 + 0.70 * intensidade_pandemia)  # Até 1.7x mais venda no auge

        # 2. EFEITO CALOR / LAVA-RÁPIDOS PRÓXIMOS (produtos automotivos e lavagem externa)
        if p["automotivo"]:
            if temp_max >= 28.0:
                w[i] *= 1.65  # Dias muito quentes de sol: lava-rápidos lotados
            elif temp_max >= 25.0:
                w[i] *= 1.25
            elif temp_max < 20.0:
                w[i] *= 0.65  # Dias frios/chuvosos: queda na lavagem automotiva

        # 3. SURTO DE DENGUE (Fev a Maio de 2024): corrida por Água Sanitária e Desinfetantes
        if d.year == 2024 and 2 <= d.month <= 5:
            if "Água Sanitária" in nome or "Desinfetante" in nome or "Odorizador" in nome:
                w[i] *= 1.35

    return w / w.sum()


def calibrar_gama(produtos):
    itens = sum(n * p for n, p in P_ITENS)
    qtd = 1 + P_QTD2
    escala = (1 + INFLACAO_ANUAL) ** -0.5
    preco = np.array([p["preco"] for p in produtos]) * escala
    pop = np.array([POPULARIDADE.get(p["nome"], 1.0) for p in produtos])

    def ticket(g):
        w = pop * preco ** (-g)
        return itens * qtd * float((w * preco).sum() / w.sum())

    lo, hi = -1.0, 4.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ticket(mid) > TICKET_ALVO else (lo, mid)
    return (lo + hi) / 2


def hora_aleatoria(rng, d):
    u = rng.random()
    if u < .25:
        h = 8 + rng.random() * 3
    elif u < .55:
        h = 11 + rng.random() * 2
    elif u < .85:
        h = 14 + rng.random() * 3
    else:
        h = 18 + rng.random() * 2
    return datetime(d.year, d.month, d.day) + timedelta(hours=h)


# =============================================================================
# 4. SIMULAÇÃO PRINCIPAL
# =============================================================================
def simular():
    rng = np.random.default_rng(SEED)
    produtos, frag = ler_cadastro()
    n_prod = len(produtos)
    lojas = list(PARTICIPACAO_LOJA)

    data_inicio = DATA_INICIO
    dias = [data_inicio + timedelta(i) for i in range((DATA_FIM - data_inicio).days + 1)]

    temperaturas = gerar_serie_temperaturas(dias, rng)
    gama = calibrar_gama(produtos)
    pesos_mes, pesos_medio = pesos_produtos_base(produtos, gama)

    # Calibra nível base de pedidos/dia para que os últimos 12 meses batam PEDIDOS_MES * 12
    ultimos = [d for d in dias if d > DATA_FIM - timedelta(days=365)]
    base_dia = PEDIDOS_MES * 12 / sum(fator_dia(d) for d in ultimos)

    # Choques semanais independentes por loja.
    # Cada semana recebe um sorteio próprio: uma semana forte não torna a próxima
    # automaticamente forte. A distribuição lognormal mantém os multiplicadores
    # positivos e aproximadamente centrados em 1.
    #
    # IMPORTANTE: as semanas começam na segunda-feira, igual ao agrupamento
    # usado no script de previsão. Isso evita misturar dois choques numa mesma
    # semana de análise.
    inicio_semana = data_inicio - timedelta(days=data_inicio.weekday())
    n_sem = ((dias[-1] - inicio_semana).days // 7) + 1
    choque = {}
    for l in lojas:
        choque[l] = rng.lognormal(
            mean=-(CHOQUE_SEMANAL_SIGMA ** 2) / 2,
            sigma=CHOQUE_SEMANAL_SIGMA,
            size=n_sem
        )

    # Configuração de estoque mínimo e alvo
    itens_medio = sum(n * p for n, p in P_ITENS) * (1 + P_QTD2)
    estoque, minimo, alvo, pendente = {}, {}, {}, defaultdict(int)
    for l in lojas:
        for i, p in enumerate(produtos):
            taxa = base_dia * PARTICIPACAO_LOJA[l] * itens_medio * pesos_medio[i]
            k = (p["cod"], l)
            minimo[k] = max(MINIMO_PISO, math.ceil(taxa * COBERTURA_MINIMO_DIAS))
            alvo[k] = minimo[k] + max(12, math.ceil(taxa * COBERTURA_REPOSICAO_DIAS))
            # Loja 1 já começa com estoque; Loja 2 começa zerada e recebe na inauguração
            estoque[k] = alvo[k] if l == 1 else 0

    pedidos, itens, movs, perdidas = [], [], [], []
    ultimo_mov = {}
    n_venda = n_det = 0

    def mov(ts, k, tipo, qtd, cod_venda, motivo):
        movs.append((len(movs) + 1, k[0], k[1], tipo, qtd, cod_venda, motivo, ts))
        ultimo_mov[k] = ts

    # Estoque inicial da Loja 1 (Matriz) no dia 1 da simulação
    ini_loja1 = datetime(data_inicio.year, data_inicio.month, data_inicio.day, 7, 0)
    for k in estoque:
        if k[1] == 1:
            mov(ini_loja1, k, "ENTRADA", estoque[k], None, "Estoque inicial")

    chegadas = defaultdict(list)
    for d in dias:
        # 0) Inauguração da Loja 2: abastece o estoque inicial no dia de abertura
        if d == DATA_ABERTURA_LOJA_2:
            ts_abertura = datetime(d.year, d.month, d.day, 7, 0)
            for p in produtos:
                k = (p["cod"], 2)
                estoque[k] = alvo[k]
                mov(ts_abertura, k, "ENTRADA", estoque[k], None, "Estoque inicial (inauguração Loja 2)")

        # 1) Chegada de mercadoria dos fornecedores
        for (k, q) in chegadas.pop(d, []):
            estoque[k] += q
            pendente[k] -= q
            mov(datetime(d.year, d.month, d.day, 7), k, "ENTRADA", q, None, "Reposição (fornecedor)")

        # 2) Revisão semanal de estoque (toda segunda-feira para lojas já abertas)
        if d.weekday() == REVISAO_DIA_SEMANA and d != data_inicio:
            for k in estoque:
                cod_prod, cod_loja = k
                if cod_loja == 2 and d < DATA_ABERTURA_LOJA_2:
                    continue
                posicao = estoque[k] + pendente[k]
                if posicao <= minimo[k]:
                    q = alvo[k] - posicao
                    prazo = int(rng.integers(PRAZO_ENTREGA[0], PRAZO_ENTREGA[1] + 1))
                    chegadas[d + timedelta(days=prazo)].append((k, q))
                    pendente[k] += q

        # 3) Sorteio de pedidos do dia nas lojas ativas
        semana = (d - inicio_semana).days // 7
        temp_hoje = temperaturas[d]
        pesos_hoje = ajustar_pesos_no_dia(pesos_mes[d.month], produtos, d, temp_hoje)
        formas_pag, probs_pag = probabilidades_pagamento_no_dia(d)

        # Em dias de muito calor (>27°C), o movimento geral também ganha um leve impulso (+5%)
        impulso_clima = 1.05 if temp_hoje >= 27.0 else (0.95 if temp_hoje < 19.0 else 1.0)

        candidatos = []
        for l in lojas:
            part_loja = participacao_loja_no_dia(l, d)
            if part_loja <= 0:
                continue
            media = base_dia * part_loja * fator_dia(d) * impulso_clima * choque[l][semana]
            media *= rng.gamma(RUIDO_DIARIO_FORMA, 1 / RUIDO_DIARIO_FORMA)
            for _ in range(int(rng.poisson(media))):
                candidatos.append((hora_aleatoria(rng, d), l))
        candidatos.sort(key=lambda c: c[0])

        for ts, l in candidatos:
            n_itens = int(rng.choice([n for n, _ in P_ITENS], p=[p for _, p in P_ITENS]))
            escolhidos = rng.choice(n_prod, size=n_itens, replace=False, p=pesos_hoje)
            linhas = []
            for i in escolhidos:
                p = produtos[int(i)]
                qtd = 2 if rng.random() < P_QTD2 else 1
                k = (p["cod"], l)
                if estoque[k] < qtd:
                    perdidas.append((ts, l, p["cod"], qtd, estoque[k]))
                    continue
                linhas.append((p, qtd, k))
            if not linhas:
                continue

            n_venda += 1
            elegiveis = [c for c in COLAB_LOJA[l] if ADMISSAO[c] <= d] or [COLAB_DONO]
            colab = int(rng.choice(elegiveis))
            forma = int(rng.choice(formas_pag, p=probs_pag))
            total = 0.0
            for idx_item, (p, qtd, k) in enumerate(linhas):
                preco = preco_em(p["preco"], d)
                total += preco * qtd
                estoque[k] -= qtd
                n_det += 1
                f = frag.get(p["cod"])
                cod_frag = int(rng.choice(f)) if f else FRAGRANCIA_PADRAO
                # Recomendação só ocorre quando o cliente leva mais de 1 item no carrinho
                foi_recomendado = bool(idx_item > 0 and rng.random() < (P_RECOMENDACAO * 3))
                itens.append((n_det, p["cod"], qtd, preco, n_venda, cod_frag, foi_recomendado))
                mov(ts, k, "SAIDA", qtd, n_venda, None)
            total = round(total, 2)
            recebido = math.ceil(total / 10) * 10 if forma == 4 else total
            pedidos.append((n_venda, l, colab, forma, total, recebido, round(recebido - total, 2), ts))

    # 4) Cenário final de teste para o frontend (reduz alguns estoques para alerta)
    fim = datetime(DATA_FIM.year, DATA_FIM.month, DATA_FIM.day, 23, 59)
    chaves = list(estoque)
    ordem = rng.permutation(len(chaves))
    n_zer = int(rng.integers(N_ZERADOS[0], N_ZERADOS[1] + 1))
    n_crit = math.ceil(len(chaves) * PCT_CRITICO)
    n_baixo = math.ceil(len(chaves) * PCT_BAIXO)
    for pos, idx in enumerate(ordem):
        k = chaves[int(idx)]
        if pos < n_zer:
            novo = 0
        elif pos < n_zer + n_crit:
            novo = int(rng.integers(1, 6))
        elif pos < n_zer + n_crit + n_baixo:
            novo = int(rng.integers(6, 16))
        else:
            continue
        if novo < estoque[k]:
            mov(fim, k, "SAIDA", estoque[k] - novo, None, "Ajuste de inventário")
            estoque[k] = novo

    # Validação de integridade contábil do estoque
    saldo = defaultdict(int)
    for _, p, l, tipo, q, _, _, _ in movs:
        saldo[(p, l)] += q if tipo == "ENTRADA" else -q
    assert all(saldo[k] == estoque[k] for k in estoque), "movimentações não fecham com o estoque"
    assert all(v >= 0 for v in estoque.values()), "estoque negativo"

    estoque_final = [
        (k[0], k[1], estoque[k], minimo[k], ultimo_mov[k])
        for k in sorted(estoque, key=lambda x: (x[1], x[0]))
    ]
    meta = {
        "seed": SEED,
        "data_inicio": data_inicio.isoformat(),
        "data_fim": DATA_FIM.isoformat(),
        "data_abertura_loja_2": DATA_ABERTURA_LOJA_2.isoformat(),
        "gama_preco_calibrado": round(gama, 4),
        "base_pedidos_dia": round(base_dia, 3),
        "choque_semanal_sigma": CHOQUE_SEMANAL_SIGMA,
        "modelo_choque_semanal": "lognormal_independente_por_loja_semana",
        "inicio_semana": "segunda-feira",
        "pedidos": len(pedidos),
        "itens": len(itens),
        "vendas_perdidas": len(perdidas),
    }
    return pedidos, itens, movs, perdidas, estoque_final, meta, produtos


# =============================================================================
# 5. GRAVAÇÃO DOS ARQUIVOS CSV
# =============================================================================
def fmt(v):
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return f"{v:.2f}"
    return "" if v is None else v


def gravar(nome, cab, linhas):
    with open(SAIDA / nome, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cab)
        for r in linhas:
            w.writerow([fmt(v) for v in r])


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    pedidos, itens, movs, perdidas, est, meta, produtos = simular()

    gravar("registro_pedido.csv", ["cod_venda", "cod_loja", "cod_colaborador", "cod_forma_pag",
                                   "valor_total", "valor_recebido", "troco", "hora_do_registro"], pedidos)
    gravar("detalhes_pedido.csv", ["cod_detalhes", "cod_produto", "quantidade", "preco_unitario",
                                   "cod_venda", "cod_fragrancia", "is_recomendacao"], itens)
    gravar("movimentacao_estoque.csv", ["cod_movimentacao", "cod_produto", "cod_loja", "tipo_movimentacao",
                                        "quantidade", "cod_venda", "motivo", "data_movimentacao"], movs)
    gravar("estoque_final.csv", ["cod_produto", "cod_loja", "quantidade_atual", "estoque_minimo",
                                 "atualizado_em"], est)
    gravar("vendas_perdidas.csv", ["hora", "cod_loja", "cod_produto", "quantidade_pedida",
                                   "quantidade_em_estoque"], perdidas)
    (SAIDA / "parametros_usados.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    ult = datetime(DATA_FIM.year, DATA_FIM.month, DATA_FIM.day) - timedelta(days=365)
    p12 = [p for p in pedidos if p[7] > ult]
    print(f"Período: {meta['data_inicio']} a {meta['data_fim']} (6 anos | semente {SEED})")
    print(f"Inauguração Loja 2: {meta['data_abertura_loja_2']}")
    print(f"Pedidos totais: {len(pedidos):,} | Itens: {len(itens):,} | Vendas perdidas: {len(perdidas):,}")
    if p12:
        print(f"Últimos 12 meses: {len(p12) / 12:.0f} pedidos/mês | Ticket médio: R$ {sum(p[4] for p in p12) / len(p12):.2f}")
    else:
        print("Últimos 12 meses: nenhum pedido gerado.")
    print(f"Arquivos gravados com sucesso em: {SAIDA}")


if __name__ == "__main__":
    main()