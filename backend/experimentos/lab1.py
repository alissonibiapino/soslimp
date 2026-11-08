import sys
import numpy as np
import pandas as pd
from scipy import stats

# CSV = sys.argv[1] if len(sys.argv) > 1 else "detalhes_pedido.csv"
CSV = "../database/gerar_banco/dados/detalhes_pedido.csv"
CONF, MU0, MARGEM_REL, SEED = 0.95, 14.00, 0.05, 42

# 1. População: ticket (valor total) de cada venda
df = pd.read_csv(CSV)
df["valor_item"] = df["quantidade"] * df["preco_unitario"]
ticket = df.groupby("cod_venda")["valor_item"].sum()
N, mu, sigma = len(ticket), ticket.mean(), ticket.std(ddof=0)
print(f"População: N={N} | média={mu:.2f} | desvio padrão={sigma:.2f}")

# 2. Tamanho da amostra (com correção para população finita)
z = stats.norm.ppf(1 - (1 - CONF) / 2)
E = MARGEM_REL * mu
n0 = (z * sigma / E) ** 2
n = int(np.ceil(n0 / (1 + (n0 - 1) / N)))
print(f"Margem de erro E={E:.2f} | z={z:.3f} | n0={n0:.1f} | n={n}")

# 3. Amostra aleatória reprodutível
amostra = ticket.sample(n=n, random_state=SEED)
xbar, s = amostra.mean(), amostra.std(ddof=1)

# 4. Intervalo de confiança para a média (t de Student)
ep = s / np.sqrt(n)
t_crit = stats.t.ppf(1 - (1 - CONF) / 2, df=n - 1)
ic = (xbar - t_crit * ep, xbar + t_crit * ep)
print(f"Amostra: média={xbar:.2f} | s={s:.2f} | erro-padrão={ep:.3f}")
print(f"IC {CONF:.0%}: [{ic[0]:.2f}; {ic[1]:.2f}]")

# 5. Teste de hipóteses: H0: mu = MU0 vs H1: mu != MU0
t_stat, p = stats.ttest_1samp(amostra, MU0)
print(f"Teste t: t={t_stat:.3f} | p-valor={p:.4f} | alfa={1-CONF:.2f}")
print("Decisão:", "rejeita H0" if p < 1 - CONF else "não rejeita H0")