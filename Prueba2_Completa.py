# %%
from pathlib import Path
import urllib.request
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from IPython.display import display

pd.options.display.float_format = "{:,.6f}".format
plt.rcParams.update({"figure.figsize": (9, 6), "axes.grid": True, "grid.alpha": 0.25})

# %%
NOMBRE_CSV = "Prueba2_2026S2_acciones.csv"
REVISION = "80fb1dc276e281dffbd8e299e2ab8bb09ea1c965"
HASH_CSV = "df17552470653dbe083b64fca155051ee563ff33703288490d84c0a4a4368e72"
URL_CSV = f"https://raw.githubusercontent.com/eldiegoveliz/AssetPricing-P2/{REVISION}/{NOMBRE_CSV}"

# Admite el nombre original y la misma escritura en minúsculas al subir el archivo.
carpetas = [Path.cwd(), Path.cwd() / "datos", Path("/workspace/AssetPricing-P2")]
candidatos = [carpeta / nombre for carpeta in carpetas for nombre in [NOMBRE_CSV, NOMBRE_CSV.lower()]]
ruta_csv = next((p for p in candidatos if p.is_file()), None)
if ruta_csv is None:
    with urllib.request.urlopen(URL_CSV, timeout=45) as respuesta:
        contenido = respuesta.read()
    if hashlib.sha256(contenido).hexdigest() != HASH_CSV:
        raise ValueError("La descarga no coincide con el archivo original. Revisa la fuente.")
    ruta_csv = Path(NOMBRE_CSV)
    ruta_csv.write_bytes(contenido)

if hashlib.sha256(ruta_csv.read_bytes()).hexdigest() != HASH_CSV:
    raise ValueError("El CSV difiere del archivo original del repositorio usado para esta pregunta. Revisa el dato.")

precios = pd.read_csv(ruta_csv, parse_dates=["Date"]).set_index("Date").sort_index()
ACCIONES = ["AAPL", "JPM", "XOM", "JNJ", "PG", "HD", "CAT", "NEE", "VZ", "SHW"]
assert set(precios.columns) == set(ACCIONES + ["SPY"])
assert precios.index.is_unique and precios.index.notna().all()
assert precios.notna().all().all() and (precios > 0).all().all()
assert precios.index.to_period("M").is_unique
assert np.all(np.diff(precios.index.to_period("M").asi8) == 1), "Hay meses faltantes."

# El primer precio no produce un retorno. No se rellenan precios ni retornos.
retornos = precios.pct_change(fill_method=None).iloc[1:]
R = retornos[ACCIONES].copy()
mercado = retornos["SPY"].copy()
assert R.notna().all().all() and mercado.notna().all()
assert R.shape[1] == 10 and "SPY" not in R.columns
T = len(R)
print(f"{len(precios)} precios mensuales; {T} retornos mensuales por serie.")
print(f"Retornos: {R.index.min().date()} a {R.index.max().date()}.")
print("Diez acciones:", ", ".join(ACCIONES), "| Mercado: SPY")
display(R.head())

# %%
media_mensual = R.mean()
desv_mensual = R.std(ddof=1)
media_anual = media_mensual * 12
desv_anual = desv_mensual * np.sqrt(12)

tabla_a = pd.DataFrame({
    "retorno_promedio_mensual_pct": 100 * media_mensual,
    "desv_estandar_mensual_pct": 100 * desv_mensual,
    "retorno_promedio_anual_pct": 100 * media_anual,
    "desv_estandar_anual_pct": 100 * desv_anual,
})
tabla_a.index.name = "accion"
display(tabla_a.round(4))

mas_riesgosa = desv_anual.idxmax()
menos_riesgosa = desv_anual.idxmin()
print(f"a.i — Mayor riesgo total: {mas_riesgosa}, desviación anual = {desv_anual[mas_riesgosa]:.4%}.")
print(f"a.i — Menor riesgo total: {menos_riesgosa}, desviación anual = {desv_anual[menos_riesgosa]:.4%}.")

fig, ax = plt.subplots()
ax.scatter(desv_anual, media_anual, s=55)
for accion in ACCIONES:
    ax.annotate(accion, (desv_anual[accion], media_anual[accion]), xytext=(5, 5), textcoords="offset points")
ax.set(xlabel="Desviación estándar anualizada: riesgo total", ylabel="Retorno promedio anualizado",
       title="a. Media y riesgo total de las diez acciones")
ax.xaxis.set_major_formatter(PercentFormatter(1))
ax.yaxis.set_major_formatter(PercentFormatter(1))
plt.tight_layout()
plt.show()

# %%
filas_dominancia = []
for a in ACCIONES:
    for b in ACCIONES:
        if a == b:
            continue
        domina = ((media_anual[a] >= media_anual[b]) and (desv_anual[a] <= desv_anual[b])
                  and ((media_anual[a] > media_anual[b]) or (desv_anual[a] < desv_anual[b])))
        if domina:
            filas_dominancia.append({
                "dominante": a, "dominada": b,
                "media_dominante_anual_pct": 100 * media_anual[a],
                "media_dominada_anual_pct": 100 * media_anual[b],
                "desv_dominante_anual_pct": 100 * desv_anual[a],
                "desv_dominada_anual_pct": 100 * desv_anual[b],
            })
tabla_dominancia = pd.DataFrame(filas_dominancia)
display(tabla_dominancia.round(4))
if not tabla_dominancia.empty:
    dominadas = set(tabla_dominancia["dominada"])
    no_dominadas = [a for a in ACCIONES if a not in dominadas]
    print("a.ii — Dos ejemplos calculados:")
    for _, fila in tabla_dominancia.head(2).iterrows():
        print(f"{fila['dominante']} domina a {fila['dominada']}: "
              f"media {fila['media_dominante_anual_pct']:.4f}% frente a {fila['media_dominada_anual_pct']:.4f}%; "
              f"desviación {fila['desv_dominante_anual_pct']:.4f}% frente a {fila['desv_dominada_anual_pct']:.4f}%.")
    print("No dominadas por otra acción individual:", no_dominadas)
else:
    print("No hay dominancia entre acciones individuales en esta muestra.")

# %%
cov_mensual = R.cov(ddof=1)
corr_mensual = R.corr()
print("Matriz de varianzas y covarianzas MENSUALES, retornos en decimales:")
display(cov_mensual)
print("Matriz de correlaciones de retornos MENSUALES:")
display(corr_mensual)

pares = pd.DataFrame([
    {"accion_1": a, "accion_2": b, "correlacion": corr_mensual.loc[a, b]}
    for i, a in enumerate(ACCIONES) for b in ACCIONES[i + 1:]
])
assert len(pares) == 45
correlacion_promedio = pares["correlacion"].mean()
par_minimo = pares.loc[pares["correlacion"].idxmin()]
par_maximo = pares.loc[pares["correlacion"].idxmax()]
print(f"b.i — Correlación promedio de {len(pares)} pares únicos: {correlacion_promedio:.6f}")
print(f"b.ii — Mínima: {par_minimo['correlacion']:.6f}, entre {par_minimo['accion_1']} y {par_minimo['accion_2']}.")
print(f"b.ii — Máxima: {par_maximo['correlacion']:.6f}, entre {par_maximo['accion_1']} y {par_maximo['accion_2']}.")
display(pares.sort_values("correlacion").reset_index(drop=True))

# %%
# OLS vectorial de las diez acciones con intercepto. Sin tasa libre de riesgo.
X = np.column_stack([np.ones(T), mercado.to_numpy()])
Y = R.to_numpy()
coeficientes = np.linalg.lstsq(X, Y, rcond=None)[0]
interceptos = pd.Series(coeficientes[0], index=ACCIONES)
betas = pd.Series(coeficientes[1], index=ACCIONES, name="beta")
residuos = pd.DataFrame(Y - X @ coeficientes, index=R.index, columns=ACCIONES)

var_mercado_m = mercado.var(ddof=1)
var_total_m = R.var(ddof=1)
var_sist_m = betas.pow(2) * var_mercado_m
var_idio_m = residuos.var(ddof=1)
porcentaje_idio = 100 * var_idio_m / var_total_m

assert np.allclose(var_total_m, var_sist_m + var_idio_m, rtol=1e-10, atol=1e-12)
assert np.allclose(betas, R.apply(lambda serie: serie.cov(mercado)) / var_mercado_m)
assert np.allclose(residuos.mean(), 0, atol=1e-12)
assert np.allclose(residuos.apply(lambda serie: serie.cov(mercado)), 0, atol=1e-12)

tabla_c_mensual = pd.DataFrame({
    "beta": betas, "var_total_mensual": var_total_m,
    "var_sistematica_mensual": var_sist_m, "var_idiosincratica_mensual": var_idio_m,
    "porcentaje_varianza_idiosincratica": porcentaje_idio,
})
tabla_c_anual = pd.DataFrame({
    "beta": betas, "var_total_anual": var_total_m * 12,
    "var_sistematica_anual": var_sist_m * 12, "var_idiosincratica_anual": var_idio_m * 12,
    "porcentaje_varianza_idiosincratica": porcentaje_idio,
})
tabla_c_mensual.index.name = tabla_c_anual.index.name = "accion"
print("Descomposición MENSUAL; varianzas en unidades de retorno decimal al cuadrado:")
display(tabla_c_mensual)
print("La misma descomposición ANUALIZADA; varianzas mensuales × 12:")
display(tabla_c_anual)

mayor_idio = porcentaje_idio.idxmax()
menor_idio = porcentaje_idio.idxmin()
promedio_porcentaje_idio = porcentaje_idio.mean()  # Media simple de los diez porcentajes, no un cociente de sumas.
print(f"c — Mayor % idiosincrático: {mayor_idio}; beta = {betas[mayor_idio]:.6f}; % idio = {porcentaje_idio[mayor_idio]:.4f}%.")
print(f"c — Menor % idiosincrático: {menor_idio}; beta = {betas[menor_idio]:.6f}; % idio = {porcentaje_idio[menor_idio]:.4f}%.")
print(f"c — Promedio simple del % idiosincrático de las diez acciones: {promedio_porcentaje_idio:.4f}%.")
print("Identidad verificada: var_total = var_sistemática + var_idiosincrática para cada acción.")

# %%
desv_idio_anual = np.sqrt(var_idio_m * 12)
tabla_d = pd.DataFrame({
    "retorno_promedio_anual_pct": 100 * media_anual,
    "desv_idiosincratica_anual_pct": 100 * desv_idio_anual,
    "porcentaje_varianza_idiosincratica": porcentaje_idio,
})
tabla_d.index.name = "accion"
display(tabla_d.round(4))

correlacion_retorno_idio = media_anual.corr(desv_idio_anual)
print(f"Correlación descriptiva entre las diez medias y sus desviaciones idiosincráticas: {correlacion_retorno_idio:.6f}.")
fig, ax = plt.subplots()
ax.scatter(desv_idio_anual, media_anual, s=55)
for accion in ACCIONES:
    ax.annotate(accion, (desv_idio_anual[accion], media_anual[accion]), xytext=(5, 5), textcoords="offset points")
# Recta únicamente descriptiva; no es una relación de valorización ni un efecto causal.
pendiente, constante = np.polyfit(desv_idio_anual, media_anual, 1)
xx = np.linspace(desv_idio_anual.min(), desv_idio_anual.max(), 100)
ax.plot(xx, constante + pendiente * xx, "--", alpha=0.6, label="Ajuste descriptivo entre diez acciones")
ax.set(xlabel="Desviación estándar idiosincrática anualizada", ylabel="Retorno promedio anualizado",
       title="d. Retorno promedio y riesgo idiosincrático")
ax.xaxis.set_major_formatter(PercentFormatter(1))
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.legend(fontsize=8)
plt.tight_layout()
plt.show()

# %%
assert T == 120 and len(ACCIONES) == 10
assert np.allclose(np.diag(cov_mensual), var_total_m)
assert np.allclose(desv_anual.pow(2), var_total_m * 12)
assert np.allclose(tabla_c_anual["var_total_anual"],
                   tabla_c_anual["var_sistematica_anual"] + tabla_c_anual["var_idiosincratica_anual"])
R2 = 1 - residuos.pow(2).sum() / ((R - R.mean()).pow(2).sum())
assert np.allclose(porcentaje_idio / 100, 1 - R2)
assert porcentaje_idio.between(0, 100).all()
assert len(pares) == 45 and (pares["accion_1"] != pares["accion_2"]).all()

carpeta_resultados = Path("resultados_pregunta1")
carpeta_resultados.mkdir(exist_ok=True)
tablas = {
    "a_retornos_y_riesgo": tabla_a, "a_dominancia": tabla_dominancia,
    "b_covarianzas_mensuales": cov_mensual, "b_correlaciones_mensuales": corr_mensual,
    "b_45_pares": pares, "c_descomposicion_mensual": tabla_c_mensual,
    "c_descomposicion_anual": tabla_c_anual, "d_retorno_y_riesgo_idiosincratico": tabla_d,
    "retornos_simples_mensuales_10_acciones": R,
}
for nombre, tabla in tablas.items():
    tabla.to_csv(carpeta_resultados / f"{nombre}.csv", encoding="utf-8-sig")
print("Controles: OK. Exportadas", len(tablas), "tablas a resultados_pregunta1/.")
print("No se usó tasa libre de riesgo ni ningún otro archivo de datos.")

# %%
from IPython.display import Markdown

display(Markdown(f"""
**1.a.i.** La acción más riesgosa es **{mas_riesgosa}**, con desviación estándar anualizada de
**{desv_anual[mas_riesgosa]:.4%}**; la menos riesgosa es **{menos_riesgosa}**, con **{desv_anual[menos_riesgosa]:.4%}**.

**1.a.ii. Dos ejemplos de dominancia media-varianza:**
- **JPM domina a XOM**: retorno medio anualizado {media_anual['JPM']:.4%} frente a {media_anual['XOM']:.4%},
  y desviación anualizada {desv_anual['JPM']:.4%} frente a {desv_anual['XOM']:.4%}.
- **NEE domina a HD**: retorno medio anualizado {media_anual['NEE']:.4%} frente a {media_anual['HD']:.4%},
  y desviación anualizada {desv_anual['NEE']:.4%} frente a {desv_anual['HD']:.4%}.
En ambos casos la dominante tiene mayor media y menor desviación en este período.

**1.b.** La correlación promedio de los 45 pares únicos es **{correlacion_promedio:.6f}**.
La mínima es **{par_minimo['correlacion']:.6f}**, entre **{par_minimo['accion_1']} y {par_minimo['accion_2']}**;
la máxima es **{par_maximo['correlacion']:.6f}**, entre **{par_maximo['accion_1']} y {par_maximo['accion_2']}**.
Las correlaciones inferiores a uno permiten reducir riesgo mediante combinaciones de activos. Los beneficios
son potencialmente mayores para pares con menor correlación, dadas sus volatilidades y sus pesos. No se
elimina el riesgo común ni se garantiza que todas las combinaciones sean menos riesgosas que cada acción.

**1.c.** El mayor porcentaje idiosincrático corresponde a **{mayor_idio}**, con beta **{betas[mayor_idio]:.6f}**
y **{porcentaje_idio[mayor_idio]:.4f}%** de su varianza. El menor corresponde a **{menor_idio}**, con beta
**{betas[menor_idio]:.6f}** y **{porcentaje_idio[menor_idio]:.4f}%**. La media simple de los diez porcentajes
es **{promedio_porcentaje_idio:.4f}%**. Una parte relevante de la varianza individual queda sin explicar por SPY;
la diversificación puede reducirla si los residuos no están perfectamente correlacionados. Esto no equivale
al porcentaje idiosincrático de una cartera, y el residuo puede incluir factores comunes omitidos.

**1.d.** Según CAPM, el riesgo idiosincrático es diversificable y no recibe una prima independiente:
el riesgo remunerado es la exposición sistemática. En el gráfico se observa una asociación positiva entre
las medias históricas y las desviaciones idiosincráticas, con correlación **{correlacion_retorno_idio:.6f}**.
Por tanto, el gráfico no muestra ausencia de asociación bruta ni reproduce la dirección negativa de la anomalía
de baja volatilidad idiosincrática discutida en clases. Sin embargo, esa asociación no demuestra que se
remunere el riesgo idiosincrático ni rechaza CAPM: son diez medias realizadas, sin controlar beta u otros factores,
y la teoría no exige que la correlación bruta sea exactamente cero. El contraste con la evidencia de clases
debe considerar sus universos, períodos y métodos distintos.
"""))

# %%
p2_estimacion = R.loc["2016-01-01":"2020-12-31"].copy()
p2_evaluacion = R.loc["2021-01-01":"2025-12-31"].copy()
assert p2_estimacion.shape == (60, 10)
assert p2_evaluacion.shape == (60, 10)
assert p2_estimacion.index.to_period("M").equals(pd.period_range("2016-01", "2020-12", freq="M"))
assert p2_evaluacion.index.to_period("M").equals(pd.period_range("2021-01", "2025-12", freq="M"))
assert p2_estimacion.index.intersection(p2_evaluacion.index).empty
assert p2_estimacion.index.max() < p2_evaluacion.index.min()
assert pd.concat([p2_estimacion, p2_evaluacion]).equals(R)
assert "SPY" not in p2_estimacion.columns and "SPY" not in p2_evaluacion.columns

p2_periodos = pd.DataFrame({
    "mitad": ["Estimación", "Evaluación"],
    "primer_mes": [str(p2_estimacion.index.min().to_period("M")), str(p2_evaluacion.index.min().to_period("M"))],
    "ultimo_mes": [str(p2_estimacion.index.max().to_period("M")), str(p2_evaluacion.index.max().to_period("M"))],
    "meses": [len(p2_estimacion), len(p2_evaluacion)],
    "acciones": [p2_estimacion.shape[1], p2_evaluacion.shape[1]],
})
display(p2_periodos)

# %%
# Única matriz usada para ESTIMAR los pesos GMV: primeros 60 meses.
p2_cov_estimacion = p2_estimacion.cov(ddof=1)
p2_S = p2_cov_estimacion.to_numpy()
p2_unos = np.ones(len(ACCIONES))
assert np.linalg.eigvalsh(p2_S).min() > 0, "La matriz de estimación no es definida positiva."
p2_z = np.linalg.solve(p2_S, p2_unos)
p2_w_gmv = pd.Series(p2_z / p2_z.sum(), index=ACCIONES, name="GMV")
p2_w_igual = pd.Series(1 / len(ACCIONES), index=ACCIONES, name="1/N")
p2_pesos = pd.concat([p2_w_gmv, p2_w_igual], axis=1)
p2_pesos.index.name = "accion"

assert np.allclose(p2_pesos.sum(), 1)
# Condición de primer orden: Sigma*w es proporcional al vector de unos.
assert np.allclose(p2_S @ p2_w_gmv.to_numpy(), np.repeat(1 / p2_z.sum(), len(ACCIONES)))
p2_cortas = p2_w_gmv[p2_w_gmv < -1e-10]
p2_largas_total = p2_w_gmv[p2_w_gmv > 0].sum()
p2_cortas_total = -p2_cortas.sum()
p2_exposicion_bruta = p2_w_gmv.abs().sum()

print("Matriz de covarianzas MENSUALES de estimación, enero 2016–diciembre 2020:")
display(p2_cov_estimacion)
print("Pesos de ambas carteras en porcentaje del patrimonio (suman 100 %):")
display((100 * p2_pesos).rename(columns={"GMV": "GMV_peso_pct", "1/N": "1_N_peso_pct"}).round(4))
print(f"Suma de pesos GMV: {p2_w_gmv.sum():.8f}")
print(f"Número de posiciones cortas: {len(p2_cortas)}; acciones: {', '.join(p2_cortas.index)}.")
print(f"Exposición larga: {p2_largas_total:.4%}; exposición corta en valor absoluto: {p2_cortas_total:.4%}.")
print(f"Exposición bruta: {p2_exposicion_bruta:.4%}; exposición neta: {p2_w_gmv.sum():.4%}.")

# %%
display(Markdown(f"""
**2.a. Resultado e implementación práctica.** Hay **{len(p2_cortas)} posiciones cortas**:
**{', '.join(p2_cortas.index)}**. Los pesos negativos representan ventas cortas; los positivos suman
{p2_largas_total:.4%} del patrimonio y los cortos equivalen a {p2_cortas_total:.4%}, dejando una exposición neta del 100 %.
La exposición bruta es {p2_exposicion_bruta:.4%}.

La solución matemática puede ser difícil o costosa de implementar: vender corto exige conseguir acciones
prestadas, pagar comisiones de préstamo, aportar garantías y gestionar llamados de margen, posibles retiros
del préstamo y pérdidas potencialmente muy grandes. Los dividendos adeudados y el rebalanceo también generan
costos. Además, los pesos pueden ser sensibles al error de estimación de covarianzas y concentrarse en pocas
acciones. Por tanto, que sea la GMV estimada sin restricciones no implica que sea automáticamente implementable
o adecuada para cualquier cliente. Imponer restricciones cambiaría el problema y requeriría recalcular la cartera.
"""))

# %%
p2_retornos_estimacion = p2_estimacion @ p2_pesos
p2_retornos_evaluacion = p2_evaluacion @ p2_pesos
p2_vol_anual = pd.DataFrame({
    "Estimación 2016–2020": p2_retornos_estimacion.std(ddof=1) * np.sqrt(12),
    "Evaluación 2021–2025": p2_retornos_evaluacion.std(ddof=1) * np.sqrt(12),
})
p2_vol_anual.index.name = "cartera"

# Comprobación independiente con w' Sigma w en cada mitad.
p2_cov_evaluacion = p2_evaluacion.cov(ddof=1)
for nombre in p2_pesos:
    w = p2_pesos[nombre].to_numpy()
    assert np.isclose(p2_vol_anual.loc[nombre, "Estimación 2016–2020"], np.sqrt(12 * w @ p2_S @ w))
    assert np.isclose(p2_vol_anual.loc[nombre, "Evaluación 2021–2025"],
                      np.sqrt(12 * w @ p2_cov_evaluacion.to_numpy() @ w))
assert p2_vol_anual.loc["GMV", "Estimación 2016–2020"] <= p2_vol_anual.loc["1/N", "Estimación 2016–2020"] + 1e-12

print("Desviaciones estándar ANUALIZADAS, en porcentaje:")
display((100 * p2_vol_anual).round(4))
p2_diferencia_pp = (p2_vol_anual.loc["GMV"] - p2_vol_anual.loc["1/N"]) * 100
display(p2_diferencia_pp.rename("GMV_menos_1_N_en_puntos_porcentuales").to_frame())

ax = (100 * p2_vol_anual.T).plot.bar(rot=0, figsize=(9, 5))
ax.set(xlabel="Mitad de la muestra", ylabel="Desviación estándar anualizada (%)",
       title="2.b. Riesgo de GMV y 1/N con los mismos pesos en ambas mitades")
for barras in ax.containers:
    ax.bar_label(barras, fmt="%.2f", padding=3)
ax.legend(title="Cartera")
ax.set_ylim(0, 100 * p2_vol_anual.to_numpy().max() * 1.2)
plt.tight_layout()
plt.show()

# %%
display(Markdown(f"""
**2.b. Observación.** En la primera mitad, la volatilidad anualizada de GMV es
**{p2_vol_anual.loc['GMV', 'Estimación 2016–2020']:.4%}**, frente a
**{p2_vol_anual.loc['1/N', 'Estimación 2016–2020']:.4%}** para 1/N. Esto es esperable por construcción:
GMV minimiza la varianza usando precisamente la matriz de covarianzas de esa mitad, y 1/N es una alternativa
factible dentro del mismo problema.

En la evaluación, sin cambiar los pesos, GMV presenta una volatilidad de
**{p2_vol_anual.loc['GMV', 'Evaluación 2021–2025']:.4%}**, frente a
**{p2_vol_anual.loc['1/N', 'Evaluación 2021–2025']:.4%}** de 1/N. GMV supera a 1/N en
**{p2_diferencia_pp['Evaluación 2021–2025']:.4f} puntos porcentuales de volatilidad**: su ventaja dentro de muestra
no se mantiene fuera de muestra en este período. Esto ilustra los problemas de error de estimación e
inestabilidad de covarianzas estudiados en clases. Estos dos resultados por sí solos no permiten separar
cuánto corresponde a cada causa ni demostrar significancia estadística de la diferencia.
"""))

# %%
import json
import zipfile

assert set(p2_pesos.index) == set(ACCIONES) and "SPY" not in p2_pesos.index
assert len(p2_estimacion) == len(p2_evaluacion) == 60
assert np.allclose(p2_w_gmv.sum(), 1) and np.allclose(p2_w_igual.sum(), 1)
assert np.isfinite(p2_pesos.to_numpy()).all() and np.isfinite(p2_vol_anual.to_numpy()).all()
# Las dos dominancias utilizadas en el resumen de la pregunta 1 están comprobadas en la tabla.
assert any((fila["dominante"], fila["dominada"]) == ("JPM", "XOM") for fila in filas_dominancia)
assert any((fila["dominante"], fila["dominada"]) == ("NEE", "HD") for fila in filas_dominancia)

entrega = Path("resultados_prueba2")
entrega.mkdir(exist_ok=True)
for nombre, tabla in tablas.items():
    tabla.to_csv(entrega / f"p1_{nombre}.csv", encoding="utf-8-sig")
p2_tablas = {
    "periodos": p2_periodos,
    "covarianzas_estimacion_mensuales": p2_cov_estimacion,
    "pesos_decimales": p2_pesos,
    "pesos_porcentajes": 100 * p2_pesos,
    "volatilidades_anuales_decimales": p2_vol_anual,
    "volatilidades_anuales_porcentajes": 100 * p2_vol_anual,
    "retornos_carteras_estimacion": p2_retornos_estimacion,
    "retornos_carteras_evaluacion": p2_retornos_evaluacion,
}
for nombre, tabla in p2_tablas.items():
    tabla.to_csv(entrega / f"p2_{nombre}.csv", encoding="utf-8-sig")
parametros = {
    "unico_archivo_datos": NOMBRE_CSV,
    "revision_datos": REVISION,
    "sha256_datos": HASH_CSV,
    "acciones": ACCIONES,
    "mercado_pregunta1": "SPY",
    "tasa_libre_de_riesgo_utilizada": False,
    "anualizacion": {"media": "mensual * 12", "desviacion": "mensual * sqrt(12)", "varianza": "mensual * 12"},
    "divisor_varianzas": "T-1, incluida la varianza residual de pregunta 1",
    "estimacion_pregunta2": {"inicio": "2016-01", "fin": "2020-12", "meses": 60},
    "evaluacion_pregunta2": {"inicio": "2021-01", "fin": "2025-12", "meses": 60},
    "restriccion_GMV": "suma de pesos = 1; sin limites de posicion; ventas cortas permitidas",
    "n_posiciones_cortas_GMV": len(p2_cortas),
    "rebalanceo": "mensual; mismos vectores de pesos en ambas mitades",
    "costos_incluidos": False,
}
(entrega / "parametros.json").write_text(json.dumps(parametros, ensure_ascii=False, indent=2), encoding="utf-8")
with zipfile.ZipFile("resultados_prueba2.zip", "w", zipfile.ZIP_DEFLATED) as archivo_zip:
    for archivo in sorted(entrega.iterdir()):
        if archivo.is_file():
            archivo_zip.write(archivo, arcname=archivo.name)
print("Controles de las dos preguntas: OK.")
print("Único insumo: Prueba2_2026S2_acciones.csv. SPY excluido de las carteras. Sin rf.")
print("Exportadas", len(tablas) + len(p2_tablas), "tablas y parámetros a resultados_prueba2.zip.")