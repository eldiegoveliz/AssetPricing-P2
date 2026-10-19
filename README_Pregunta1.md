# Prueba 2 — Pregunta 1

[Abrir el cuaderno en Google Colab](https://colab.research.google.com/github/eldiegoveliz/AssetPricing-P2/blob/main/Prueba2_Pregunta1.ipynb)

El archivo `Prueba2_Pregunta1.ipynb` contiene los apartados a–d, con tablas y gráficos de una ejecución completa de sus ocho celdas de código. En Colab, selecciona **Entorno de ejecución → Ejecutar todo** para reproducir los resultados. `Prueba2_Pregunta1.py` contiene el mismo código, separado por marcadores de celda `# %%`.

Se usa únicamente `Prueba2_2026S2_acciones.csv`: diez acciones y SPY como mercado, sin incorporar SPY a las comparaciones entre acciones y sin tasa libre de riesgo. Los 121 precios generan 120 retornos simples mensuales, de enero de 2016 a diciembre de 2025.

La media mensual se anualiza multiplicando por 12, la desviación estándar por la raíz de 12 y la varianza por 12. Para la descomposición exacta del riesgo, la varianza total y la residual usan el mismo divisor muestral, T−1. La correlación promedio excluye la diagonal y considera los 45 pares únicos de acciones.

Los datos se leen del archivo local o se descargan de una revisión fija del repositorio y se verifican mediante SHA-256. La ejecución utiliza NumPy, pandas y Matplotlib, disponibles en Colab. Los resultados CSV se generan en `resultados_pregunta1/`. Las celdas de interpretación quedan disponibles para escribir las respuestas propias.
