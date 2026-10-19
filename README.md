# Asset Pricing — Prueba 2

## Cuaderno completo: preguntas 1 y 2

[Abrir Prueba2_Completa.ipynb en Google Colab](https://colab.research.google.com/github/eldiegoveliz/AssetPricing-P2/blob/main/Prueba2_Completa.ipynb)

`Prueba2_Completa.ipynb` contiene únicamente los prompts originales en celdas de texto y las celdas de código con respuestas, tablas y gráficos. Los enunciados están identificados como **PROMPT #1** y **PROMPT #2**, y se conserva la solicitud posterior de respuestas como seguimiento. Sus 16 celdas de código se ejecutaron desde un kernel nuevo sin errores. `Prueba2_Completa.py` contiene el mismo código separado por marcadores de celda `# %%`.

En Colab, selecciona **Entorno de ejecución → Ejecutar todo**, revisa las respuestas y guarda una copia con las salidas para entregar. El cuaderno exporta 17 tablas y los parámetros utilizados en `resultados_prueba2.zip`.

## Datos y convenciones

- Único insumo: `Prueba2_2026S2_acciones.csv`, leído localmente o descargado desde una revisión fija y verificado por SHA-256.
- Retornos simples mensuales de las diez acciones. SPY se usa únicamente como mercado en la pregunta 1 y no integra las carteras.
- Sin tasa libre de riesgo. Media anualizada = mensual × 12; desviación anualizada = mensual × raíz de 12; varianza anualizada = mensual × 12.
- Varianzas muestrales con divisor T−1, incluida la residual para que la descomposición del riesgo de la pregunta 1 cierre exactamente.

## Pregunta 1

Usa los 120 retornos de enero de 2016 a diciembre de 2025: media y riesgo total, dominancia media-varianza, matrices mensuales, correlaciones entre los 45 pares únicos, descomposición del riesgo respecto de SPY y relación descriptiva entre retorno promedio y riesgo idiosincrático.

## Pregunta 2

Estima GMV sin restricciones de posición usando únicamente los 60 meses de enero de 2016 a diciembre de 2020, sujeto a que los pesos sumen uno. Evalúa los mismos pesos en los 60 meses de enero de 2021 a diciembre de 2025 y compara con 1/N (10 % por acción). Los pesos se mantienen mediante rebalanceo mensual, sin costos; no se reoptimizan con los datos de evaluación.

La GMV tiene tres posiciones cortas: AAPL, XOM y SHW. Sus volatilidades anualizadas son:

| Mitad | GMV | 1/N |
|---|---:|---:|
| Estimación 2016–2020 | 10,6390 % | 13,8197 % |
| Evaluación 2021–2025 | 15,2756 % | 14,7809 % |

El cuaderno explica la implementación de las ventas cortas, la pérdida de la ventaja dentro de muestra y una recomendación condicionada por esta evidencia. Los resultados no establecen superioridad futura, mayor rentabilidad ni significancia estadística de la diferencia.

Los archivos `Prueba2_Pregunta1.ipynb`, `Prueba2_Pregunta1.py` y `README_Pregunta1.md` corresponden a la versión anterior dedicada solo a la primera pregunta. Para ambas preguntas, utiliza `Prueba2_Completa.ipynb`.
