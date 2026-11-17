import sys
import pandas as pd
import statsmodels.api as sm

df = pd.read_csv("../database/gerar_banco/dados/detalhes_pedido.csv")
df["valor_item"] = df["quantidade"] * df["preco_unitario"]
df["is_recomendacao"] = df["is_recomendacao"].astype(str).str.lower().eq("true")
v = df.groupby("cod_venda").agg(ticket=("valor_item", "sum"),
                                qtd_itens=("quantidade", "sum"),
                                tem_recomendacao=("is_recomendacao", "any"))
v["tem_recomendacao"] = v["tem_recomendacao"].astype(int)

m = sm.OLS(v["ticket"], sm.add_constant(v[["qtd_itens", "tem_recomendacao"]])).fit()
tab = pd.DataFrame({"coef": m.params, "erro_padrao": m.bse, "p_valor": m.pvalues})
tab[["ic95_inf", "ic95_sup"]] = m.conf_int()
print(tab.round(3))
print(f"\nR2={m.rsquared:.3f} | R2 aj.={m.rsquared_adj:.3f} | "
      f"F={m.fvalue:.1f} (p={m.f_pvalue:.3g}) | erro residual={m.mse_resid**0.5:.2f}")