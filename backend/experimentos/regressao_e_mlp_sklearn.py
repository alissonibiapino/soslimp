"""Comparativo de modelos para prever a demanda semanal (SOSLimp).
Modelos avaliados: Regressão Linear, MLP (scikit-learn) e RNN (PyTorch).

Como usar:
    python backend/experimentos/regressao_e_mlp_sklearn.py
"""
import random
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neural_network import MLPRegressor

warnings.filterwarnings("ignore")

# =============================================================================
# 1. CONFIGURAÇÕES E CAMINHOS DOS ARQUIVOS
# =============================================================================
PASTA_ATUAL = Path(__file__).resolve().parent
PASTA_BANCO = PASTA_ATUAL.parent / "database" / "gerar_banco"
PASTA_DADOS = PASTA_BANCO / "dados"
ARQUIVO_SQL_PRODUTOS = PASTA_BANCO / "02_dados_iniciais.sql"

N_LAGS = 4          # Quantas semanas passadas o modelo olha para prever a próxima[cite: 5]
N_SPLITS = 5        # Quantas rodadas de teste temporal vamos fazer[cite: 5]
SEMENTE = 42        # Número fixo para o resultado dar sempre igual[cite: 3, 5]


def travar_aleatoriedade():
    """Garante que o PyTorch e o NumPy gerem sempre os mesmos números."""
    random.seed(SEMENTE)
    np.random.seed(SEMENTE)
    torch.manual_seed(SEMENTE)


# =============================================================================
# 2. LEITURA E PREPARAÇÃO DOS DADOS
# =============================================================================
def buscar_categorias_dos_produtos():
    """Lê o arquivo 02_dados_iniciais.sql e descobre a categoria de cada produto."""
    texto_sql = ARQUIVO_SQL_PRODUTOS.read_text(encoding="utf-8")
    
    # Pega apenas o trecho do SQL onde estão os INSERTs da tabela produto[cite: 3]
    trecho_produtos = texto_sql.split("INSERT INTO produto (", 1)[1]
    trecho_produtos = trecho_produtos.split("INSERT INTO fragrancia", 1)[0]
    
    padrao = r"\((\d+), '([^']*)', '([^']*)', '([^']*)', ([\d.]+), '([^']*)'\)"
    linhas_encontradas = re.findall(padrao, trecho_produtos)
    
    mapa_produto_categoria = {}
    for indice, dados in enumerate(linhas_encontradas):
        cod_produto = indice + 1
        cod_categoria = int(dados[0])
        mapa_produto_categoria[cod_produto] = cod_categoria
        
    return mapa_produto_categoria


def carregar_vendas_semanais():
    """Lê os CSVs de pedidos e itens e agrupa o total vendido por semana."""
    pedidos = pd.read_csv(
        PASTA_DADOS / "registro_pedido.csv",
        usecols=["cod_venda", "cod_loja", "hora_do_registro"],
        parse_dates=["hora_do_registro"]
    )
    detalhes = pd.read_csv(
        PASTA_DADOS / "detalhes_pedido.csv",
        usecols=["cod_venda", "cod_produto", "quantidade"]
    )

    # Adiciona a coluna cod_categoria na tabela de itens vendidos
    mapa_categorias = buscar_categorias_dos_produtos()
    detalhes["cod_categoria"] = detalhes["cod_produto"].map(mapa_categorias)

    # Junta os itens com os dados do pedido (para saber a data e a loja de cada item)
    vendas = detalhes.merge(pedidos, on="cod_venda", how="inner")

    # Transforma a data da venda na segunda-feira daquela semana
    dia_da_semana = vendas["hora_do_registro"].dt.weekday
    vendas["semana_inicio"] = vendas["hora_do_registro"].dt.normalize() - pd.to_timedelta(dia_da_semana, unit="D")

    # Soma quantas unidades foram vendidas por semana, por loja e por categoria
    vendas_agrupadas = vendas.groupby(
        ["semana_inicio", "cod_loja", "cod_categoria"], as_index=False
    )["quantidade"].sum()
    vendas_agrupadas = vendas_agrupadas.rename(columns={"quantidade": "unidades"})

    # Cria uma tabela com todas as semanas (mesmo se alguma categoria vendeu 0 na semana)
    primeira_semana = vendas_agrupadas["semana_inicio"].min()
    ultima_semana = vendas_agrupadas["semana_inicio"].max()
    todas_semanas = pd.date_range(primeira_semana, ultima_semana, freq="7D")
    todas_lojas = sorted(vendas_agrupadas["cod_loja"].unique())
    todas_categorias = sorted(vendas_agrupadas["cod_categoria"].unique())

    grade_completa = pd.MultiIndex.from_product(
        [todas_semanas, todas_lojas, todas_categorias],
        names=["semana_inicio", "cod_loja", "cod_categoria"]
    ).to_frame().reset_index(drop=True)

    df = grade_completa.merge(vendas_agrupadas, on=["semana_inicio", "cod_loja", "cod_categoria"], how="left")
    df["unidades"] = df["unidades"].fillna(0.0)
    df["unidades"] = df["unidades"].fillna(0.0)

    # Ignora semanas da Loja 2 antes da inauguração dela (03/11/2023)
    df = df[~((df["cod_loja"] == 2) & (df["semana_inicio"] < "2023-11-06"))].copy()

    # Remove a primeira e a última semana porque podem ter menos de 7 dias completos
    lista_semanas = np.sort(df["semana_inicio"].unique())
    semanas_completas = lista_semanas[1:-1]
    df = df[df["semana_inicio"].isin(semanas_completas)].copy()

    df = df.sort_values(["cod_loja", "cod_categoria", "semana_inicio"]).reset_index(drop=True)
    return df


def criar_colunas_de_entrada(df):
    """Cria as variáveis (features) que os modelos vão usar para prever a demanda[cite: 5]."""
    # 1. Cria as colunas de vendas das 4 semanas anteriores (lag1 até lag4)[cite: 5]
    grupo = df.groupby(["cod_loja", "cod_categoria"])["unidades"]
    df["lag1"] = grupo.shift(1)  # 1 semana atrás
    df["lag2"] = grupo.shift(2)  # 2 semanas atrás
    df["lag3"] = grupo.shift(3)  # 3 semanas atrás
    df["lag4"] = grupo.shift(4)  # 4 semanas atrás

    # 2. Média das últimas 4 semanas[cite: 5]
    df["media4"] = (df["lag1"] + df["lag2"] + df["lag3"] + df["lag4"]) / 4.0

    # 3. Sazonalidade (representa a época do ano usando seno e cosseno da semana)[cite: 5]
    numero_semana_ano = df["semana_inicio"].dt.isocalendar().week.astype(int)
    df["sen_sem"] = np.sin(2 * np.pi * numero_semana_ano / 52)
    df["cos_sem"] = np.cos(2 * np.pi * numero_semana_ano / 52)

    # Remove as 4 primeiras semanas que ficaram vazias (NaN) por não terem histórico anterior[cite: 5]
    df = df.dropna(subset=["lag1", "lag2", "lag3", "lag4"]).reset_index(drop=True)

    # 4. Transforma o código da loja e da categoria em colunas de 0 e 1 (One-Hot Encoding)[cite: 5]
    colunas_loja = pd.get_dummies(df["cod_loja"], prefix="loja", dtype=float)
    colunas_categoria = pd.get_dummies(df["cod_categoria"], prefix="cat", dtype=float)

    # Contexto fixo da linha: época do ano + qual é a loja + qual é a categoria[cite: 5]
    df_contexto = pd.concat([df[["sen_sem", "cos_sem"]], colunas_loja, colunas_categoria], axis=1)
    matriz_contexto = df_contexto.to_numpy(dtype=float)

    # -------------------------------------------------------------------------
    # FORMATO 2D (Tabela normal para Regressão Linear e MLP do scikit-learn)[cite: 5]
    # -------------------------------------------------------------------------
    colunas_numericas = ["lag1", "lag2", "lag3", "lag4", "media4"]
    X_tabela_2d = np.hstack([df[colunas_numericas].to_numpy(dtype=float), matriz_contexto])

    # -------------------------------------------------------------------------
    # FORMATO 3D (Sequência no tempo para a RNN do PyTorch)
    # Formato exigido pela RNN: (total_de_exemplos, 4_semanas, colunas)
    # -------------------------------------------------------------------------
    total_exemplos = len(df)
    total_colunas_contexto = matriz_contexto.shape[1]
    X_sequencia_3d = np.zeros((total_exemplos, N_LAGS, 1 + total_colunas_contexto), dtype=float)

    # Preenche passo a passo em ordem cronológica: da semana mais antiga (lag4) até a mais recente (lag1)
    colunas_em_ordem_cronologica = ["lag4", "lag3", "lag2", "lag1"]
    for passo_tempo, nome_coluna_lag in enumerate(colunas_em_ordem_cronologica):
        vendas_naquela_semana = df[nome_coluna_lag].to_numpy(dtype=float)
        X_sequencia_3d[:, passo_tempo, 0] = vendas_naquela_semana
        X_sequencia_3d[:, passo_tempo, 1:] = matriz_contexto

    # O que queremos prever (vendas reais da semana atual)[cite: 5]
    y_alvo = df["unidades"].to_numpy(dtype=float)

    return df, X_tabela_2d, X_sequencia_3d, y_alvo


# =============================================================================
# 3. DEFINIÇÃO DOS MODELOS E MÉTRICAS
# =============================================================================
def calcular_metricas(valores_reais, valores_previstos):
    """Calcula MAE, RMSE e R² comparando o valor real com o previsto[cite: 5]."""
    erro = valores_reais - valores_previstos
    
    mae = np.mean(np.abs(erro))
    rmse = np.sqrt(np.mean(erro ** 2))
    
    variancia_total = np.sum((valores_reais - valores_reais.mean()) ** 2)
    r2 = 1 - (np.sum(erro ** 2) / variancia_total)
    
    return {"MAE": mae, "RMSE": rmse, "R2": r2}


class ModeloRNN(nn.Module):
    """Rede Neural Recorrente simples em PyTorch."""
    def __init__(self, quantidade_entradas):
        super().__init__()
        # Camada recorrente com 16 neurônios na memória interna
        self.camada_recorrente = nn.RNN(
            input_size=quantidade_entradas,
            hidden_size=16,
            batch_first=True,
            nonlinearity="relu"
        )
        # Camada final que transforma os 16 neurônios em 1 único número (a previsão)
        self.camada_saida = nn.Linear(16, 1)

    def forward(self, x):
        # Passa as 4 semanas pela camada recorrente
        saidas_todas_semanas, _ = self.camada_recorrente(x)
        
        # Pega o resultado apenas da última semana (índice -1) para prever a próxima
        memoria_final = saidas_todas_semanas[:, -1, :]
        
        previsao = self.camada_saida(memoria_final)
        return previsao.squeeze(-1)


def treinar_e_prever_rnn(X_treino, y_treino, X_teste):
    """Treina a RNN do PyTorch e devolve as previsões para o conjunto de teste."""
    travar_aleatoriedade()

    # Converte matrizes do NumPy para Tensores do PyTorch
    tensor_x_treino = torch.tensor(X_treino, dtype=torch.float32)
    tensor_y_treino = torch.tensor(y_treino, dtype=torch.float32)
    tensor_x_teste = torch.tensor(X_teste, dtype=torch.float32)

    numero_features = X_treino.shape[2]
    modelo = ModeloRNN(quantidade_entradas=numero_features)
    
    otimizador = torch.optim.Adam(modelo.parameters(), lr=0.005, weight_decay=0.0001)
    funcao_erro = nn.MSELoss()

    # Loop de treinamento (150 épocas)
    modelo.train()
    for epoca in range(150):
        otimizador.zero_grad()                      # Zera os cálculos da época anterior
        previsoes_treino = modelo(tensor_x_treino)  # Faz a previsão
        erro = funcao_erro(previsoes_treino, tensor_y_treino)  # Calcula o erro
        erro.backward()                             # Calcula o ajuste necessário nos pesos
        otimizador.step()                           # Atualiza os pesos da rede

    # Faz a previsão final nos dados de teste
    modelo.eval()
    with torch.no_grad():
        previsoes_teste = modelo(tensor_x_teste).numpy()
        
    return previsoes_teste


# =============================================================================
# 4. EXECUÇÃO PRINCIPAL (TREINO E VALIDAÇÃO TEMPORAL)
# =============================================================================
def main():
    df_base = carregar_vendas_semanais()
    df, X_2d, X_3d, y = criar_colunas_de_entrada(df_base)
    
    total_semanas = df["semana_inicio"].nunique()
    print(f"Dataset carregado: {len(df)} linhas ({total_semanas} semanas completas)")

    semanas_unicas = np.sort(df["semana_inicio"].unique())
    divisor_temporal = TimeSeriesSplit(n_splits=N_SPLITS)
    
    resultados = []

    # Roda as 5 divisões de tempo (sempre treinando no passado e testando no futuro)[cite: 5]
    for numero_rodada, (indices_semanas_treino, indices_semanas_teste) in enumerate(divisor_temporal.split(semanas_unicas), start=1):
        semanas_treino = semanas_unicas[indices_semanas_treino]
        semanas_teste = semanas_unicas[indices_semanas_teste]

        # Descobre quais linhas da tabela pertencem ao treino e quais pertencem ao teste[cite: 5]
        tr = np.where(df["semana_inicio"].isin(semanas_treino))[0]
        te = np.where(df["semana_inicio"].isin(semanas_teste))[0]

        # Padroniza o alvo (y) usando apenas a média e desvio padrão do treino[cite: 5]
        media_y = y[tr].mean()
        desvio_y = y[tr].std()
        y_treino_padronizado = (y[tr] - media_y) / desvio_y

        # ---------------------------------------------------------------------
        # MODELOS 1 e 2: Regressão Linear e MLP (usam a tabela 2D)[cite: 5]
        # ---------------------------------------------------------------------
        media_2d = X_2d[tr].mean(axis=0)
        desvio_2d = X_2d[tr].std(axis=0)
        desvio_2d[desvio_2d == 0] = 1.0  # Evita divisão por zero[cite: 5]

        X_treino_2d = (X_2d[tr] - media_2d) / desvio_2d
        X_teste_2d = (X_2d[te] - media_2d) / desvio_2d

        # Treina Regressão Linear[cite: 5]
        modelo_regressao = LinearRegression()
        modelo_regressao.fit(X_treino_2d, y_treino_padronizado)
        prev_regressao = (modelo_regressao.predict(X_teste_2d) * desvio_y) + media_y
        resultados.append({"rodada": numero_rodada, "modelo": "1. Regressão Linear", **calcular_metricas(y[te], prev_regressao)})

        # Treina MLP (scikit-learn)[cite: 5]
        modelo_mlp = MLPRegressor(
            hidden_layer_sizes=(16, 8),
            activation="relu",
            solver="adam",
            alpha=1e-4,
            learning_rate_init=1e-3,
            max_iter=500,
            random_state=SEMENTE
        )
        modelo_mlp.fit(X_treino_2d, y_treino_padronizado)
        prev_mlp = (modelo_mlp.predict(X_teste_2d) * desvio_y) + media_y
        resultados.append({"rodada": numero_rodada, "modelo": "2. MLP (sklearn)", **calcular_metricas(y[te], prev_mlp)})

        # ---------------------------------------------------------------------
        # MODELO 3: RNN (usa a sequência 3D)
        # ---------------------------------------------------------------------
        media_3d = X_3d[tr].mean(axis=(0, 1), keepdims=True)
        desvio_3d = X_3d[tr].std(axis=(0, 1), keepdims=True)
        desvio_3d[desvio_3d == 0] = 1.0

        X_treino_3d = (X_3d[tr] - media_3d) / desvio_3d
        X_teste_3d = (X_3d[te] - media_3d) / desvio_3d

        prev_rnn_padronizada = treinar_e_prever_rnn(X_treino_3d, y_treino_padronizado, X_teste_3d)
        prev_rnn = (prev_rnn_padronizada * desvio_y) + media_y
        resultados.append({"rodada": numero_rodada, "modelo": "3. RNN (PyTorch)", **calcular_metricas(y[te], prev_rnn)})

    # Exibe as tabelas finais no terminal[cite: 5]
    tabela_resultados = pd.DataFrame(resultados)
    
    print("\n--- Métricas por rodada ---")
    print(tabela_resultados.round(3).to_string(index=False))
    
    print("\n--- Média das 5 rodadas ---")
    print(tabela_resultados.groupby("modelo")[["MAE", "RMSE", "R2"]].mean().round(3))
    
    print("\n--- Média das rodadas 3 a 5 (com histórico consolidado) ---")
    rodadas_finais = tabela_resultados[tabela_resultados["rodada"] >= 3]
    print(rodadas_finais.groupby("modelo")[["MAE", "RMSE", "R2"]].mean().round(3))


if __name__ == "__main__":
    main()