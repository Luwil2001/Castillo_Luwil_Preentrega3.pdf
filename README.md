# Compras anteriores por categoría: evidencia descriptiva para retail

## Problema de negocio
El equipo comercial quiere entender si el historial de compras previas de los clientes asociados a cada categoría presenta diferencias que justifiquen una exploración comercial más dirigida. Esta primera rebanada compara la mediana y el promedio de `PreviousPurchases` por categoría. El archivo contiene un registro por `CustomerID` y no declara una fecha transaccional; por eso este análisis no mide recompra en el tiempo ni prueba que una categoría cause mayor recurrencia.

## Stack
- Python 3
- pandas: controles de calidad y agregación
- Pillow: gráfico estático

## Fuente
Kaggle, [Store Sales](https://www.kaggle.com/datasets/hassanjameelahmed/store-sales/data). CSV `store_sales.csv` descargado desde la página pública del dataset. Para reproducir, descargá el archivo y guardalo como `data/store_sales.csv`.

## Repositorio
URL proporcionada para el repositorio: https://github.com/Luwil2001/Castillo_Luwil_Preentrega3.pdf.git

## Metodología
Se sigue CRISP-DM de forma incremental: se traduce la pregunta comercial a una métrica observable; se inspeccionan estructura, nulos, duplicados y rangos; se prepara la tabla con filas válidas; se compara por categoría; y se evalúa qué conclusiones permite la evidencia. El backlog se distribuyó en tres sprints de dos semanas, con incrementos revisables en cada sprint. Al inicio de cada sprint se valida el incremento anterior (definición de la métrica, reglas de limpieza, agregados y lectura) antes de ampliarlo.

## Hallazgos clave
- El archivo tiene 5.000 filas, 11 columnas y 9 categorías.
- En los campos de la rebanada (`Category`, `PreviousPurchases`) no se detectaron nulos; no hubo filas exactamente duplicadas. `CustomerID` aparece una vez por registro.
- La mediana de `PreviousPurchases` es 5 en las nueve categorías. Por lo tanto, la mediana no permite identificar una categoría con menor historial previo.
- Los promedios van de 4,875 en Mens Clothing a 5,238 en Home, una diferencia de 0,363 compras previas. Es una diferencia descriptiva, no evidencia causal.
- Se encontraron 6 descuentos superiores al máximo de 32% indicado en la ficha (valores 34% y 36%). El descuento no se usa para filtrar ni calcular esta rebanada y se deja como control pendiente.
- La fuente no incluye fecha de compra y cada `CustomerID` es único; no permite medir recompra temporal ni repetición de compras por cliente.

## Cómo ejecutar
1. Instalar dependencias: `python -m pip install -r requirements.txt`.
2. Descargar `store_sales.csv` desde Kaggle y guardarlo en `data/store_sales.csv`.
3. Ejecutar desde la carpeta del proyecto: `python src/analisis_recurrencia.py --input data/store_sales.csv --output results`.
4. El script genera `results/recurrencia_por_categoria.csv`, `results/control_calidad.csv` y `results/recurrencia_por_categoria.png`.

## Estructura
- `src/analisis_recurrencia.py`: limpieza mínima, validaciones, agregación y gráfico.
- `results/`: salidas reproducibles del análisis.
- `data/`: ubicación local esperada para el CSV; el archivo no se redistribuye en este repositorio.

