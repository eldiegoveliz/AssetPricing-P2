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