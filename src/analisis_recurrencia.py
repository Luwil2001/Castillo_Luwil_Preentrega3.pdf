"""Análisis descriptivo de compras anteriores por categoría.

Uso:
  python src/analisis_recurrencia.py --input data/store_sales.csv --output results
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

MIN_PREVIOUS_PURCHASES = 0
MAX_PREVIOUS_PURCHASES = 13
EXPECTED_MAX_DISCOUNT = 32  # Referencia indicada en la ficha del dataset.


def analyze(input_path: Path, output_dir: Path) -> None:
    """Valida campos de la rebanada, agrega por categoría y guarda evidencias."""
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_path)

    required = {"Category", "PreviousPurchases", "CustomerID", "DiscountApplied(%)"}
    missing_columns = required - set(df.columns)
    if missing_columns:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing_columns)}")

    # Controles de calidad antes de filtrar: solo quitamos duplicados de fila exactos.
    rows_in = len(df)
    exact_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    rows_after_dedup = len(df)

    # Una fila es válida para este corte si la categoría está informada y el
    # conteo de compras previas es numérico y está dentro del rango 0-13.
    df["PreviousPurchases"] = pd.to_numeric(df["PreviousPurchases"], errors="coerce")
    category_ok = df["Category"].notna() & df["Category"].astype(str).str.strip().ne("")
    purchases_ok = (
        df["PreviousPurchases"].notna()
        & df["PreviousPurchases"].between(MIN_PREVIOUS_PURCHASES, MAX_PREVIOUS_PURCHASES)
    )
    valid_mask = category_ok & purchases_ok
    excluded_invalid = int((~valid_mask).sum())
    valid = df.loc[valid_mask].copy()
    valid["PreviousPurchases"] = valid["PreviousPurchases"].astype(int)

    # El descuento se informa como control aparte: no se usa ni excluye en esta
    # rebanada porque la pregunta compara compras previas por categoría.
    discount = pd.to_numeric(valid["DiscountApplied(%)"], errors="coerce")
    discounts_above_reference = int((discount > EXPECTED_MAX_DISCOUNT).sum())

    summary = (
        valid.groupby("Category", as_index=False)
        .agg(
            registros=("PreviousPurchases", "size"),
            mediana=("PreviousPurchases", "median"),
            promedio=("PreviousPurchases", "mean"),
        )
        .sort_values(["mediana", "promedio", "Category"], ascending=[True, True, True])
    )
    summary["promedio"] = summary["promedio"].round(3)
    summary.to_csv(output_dir / "recurrencia_por_categoria.csv", index=False)

    quality = pd.DataFrame([
        ("filas_entrada", rows_in),
        ("columnas_entrada", df.shape[1]),
        ("duplicados_exactos_detectados_y_eliminados", exact_duplicates),
        ("filas_validas_para_la_rebanada", len(valid)),
        ("filas_excluidas_por_categoria_o_compras_previas_invalidas", excluded_invalid),
        ("nulos_en_campos_de_la_rebanada_antes_de_filtrar", int(df[["Category", "PreviousPurchases"]].isna().sum().sum())),
        ("CustomerID_unicos_en_archivo", int(df["CustomerID"].nunique(dropna=True))),
        ("IDs_de_cliente_repetidos_en_archivo", int(df["CustomerID"].duplicated().sum())),
        ("descuentos_superiores_a_32_por_ciento_en_filas_validas", discounts_above_reference),
    ], columns=["control", "valor"])
    quality.to_csv(output_dir / "control_calidad.csv", index=False)

    # Como todas las medianas empatan en 5, el gráfico muestra el promedio y
    # ordena por ese valor como criterio de lectura; la tabla conserva mediana.
    plot_df = summary.sort_values("promedio", ascending=True)
    width, height = 1800, 1120
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    font_bold_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    regular = ImageFont.truetype(str(font_path), 30) if font_path.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), 23) if font_path.exists() else ImageFont.load_default()
    bold = ImageFont.truetype(str(font_bold_path), 39) if font_bold_path.exists() else regular
    draw.text((90, 55), "El promedio de compras previas varía poco entre categorías", fill="#18324B", font=bold)
    draw.text((92, 120), "Mediana = 5 en las nueve categorías · promedio y n por categoría", fill="#536570", font=regular)
    x0, x1 = 590, 1560
    y0, step, bar_h = 220, 75, 38
    axis_min, axis_max = 4.6, 5.45
    # Escala acotada para mostrar las diferencias pequeñas; se rotula para evitar
    # que el gráfico sugiera un efecto de mayor magnitud que el observado.
    for tick in [4.6, 4.8, 5.0, 5.2, 5.4]:
        x = x0 + (tick-axis_min)/(axis_max-axis_min)*(x1-x0)
        draw.line((x, y0-25, x, y0+step*len(plot_df)-17), fill="#DCE4E8", width=2)
        draw.text((x-28, y0+step*len(plot_df)-5), f"{tick:.1f}", fill="#536570", font=small)
    median_x = x0 + (5-axis_min)/(axis_max-axis_min)*(x1-x0)
    draw.line((median_x, y0-30, median_x, y0+step*len(plot_df)-17), fill="#D98E04", width=4)
    for i, row in enumerate(plot_df.itertuples(index=False)):
        y = y0 + i*step
        draw.text((90, y+3), str(row.Category), fill="#24313A", font=regular)
        value = float(row.promedio)
        x = x0 + (value-axis_min)/(axis_max-axis_min)*(x1-x0)
        draw.rounded_rectangle((x0, y, x, y+bar_h), radius=7, fill="#247C8C")
        draw.text((x+14, y+2), f"{value:.3f}  (n={int(row.registros)})", fill="#24313A", font=small)
    draw.text((x0, y0+step*len(plot_df)+55), "Promedio de compras anteriores (eje desde 4,6; escala recortada)", fill="#536570", font=regular)
    draw.text((92, height-65), "Fuente: Kaggle Store Sales · 5.000 registros · la línea vertical marca la mediana común (5).", fill="#536570", font=small)
    image.save(output_dir / "recurrencia_por_categoria.png")

    print(f"filas={rows_in}; categorias={summary.shape[0]}; filas_validas={len(valid)}; exact_duplicates={exact_duplicates}; invalid_rows={excluded_invalid}; discount_over_32={discounts_above_reference}")
    print(summary.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Ruta al CSV store_sales.csv")
    parser.add_argument("--output", type=Path, default=Path("results"), help="Carpeta para tabla, controles y gráfico")
    args = parser.parse_args()
    analyze(args.input, args.output)


if __name__ == "__main__":
    main()

