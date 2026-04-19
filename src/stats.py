"""
Genera estadísticas y gráficas de las detecciones almacenadas en la base de datos.
Uso: py -3.11 src/stats.py
"""

import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from collections import Counter

DB_PATH  = Path("data/detections.db")
OUT_DIR  = Path("runs/stats")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def query(conn, sql):
    return conn.execute(sql).fetchall()


def main():
    with sqlite3.connect(DB_PATH) as conn:

        # ── 1. Detecciones por año ─────────────────────────────────────────
        rows = query(conn, """
            SELECT SUBSTR(p.pub_date, 1, 4) as year, COUNT(d.id)
            FROM pages p JOIN detections d ON d.page_id = p.id
            WHERE year IS NOT NULL AND year != ''
            GROUP BY year ORDER BY year
        """)
        years  = [r[0] for r in rows]
        counts = [r[1] for r in rows]

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(years, counts, color="#4C72B0")
        ax.set_title("Detecciones de vinetas por año", fontsize=14)
        ax.set_xlabel("Año")
        ax.set_ylabel("Número de viñetas detectadas")
        ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
        plt.xticks(rotation=45)
        plt.tight_layout()
        fig.savefig(OUT_DIR / "detecciones_por_anyo.png", dpi=150)
        plt.close()
        print("Grafica 1: detecciones_por_anyo.png")

        # ── 2. Distribución del número de viñetas por página ──────────────
        rows2 = query(conn, """
            SELECT COUNT(d.id) as n
            FROM pages p LEFT JOIN detections d ON d.page_id = p.id
            GROUP BY p.id
        """)
        freq = Counter(r[0] for r in rows2)
        xs = sorted(freq.keys())
        ys = [freq[x] for x in xs]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar([str(x) for x in xs], ys, color="#DD8452")
        ax.set_title("Paginas segun numero de vinetas detectadas", fontsize=14)
        ax.set_xlabel("Viñetas por página")
        ax.set_ylabel("Número de páginas")
        plt.tight_layout()
        fig.savefig(OUT_DIR / "vinetas_por_pagina.png", dpi=150)
        plt.close()
        print("Grafica 2: vinetas_por_pagina.png")

        # ── 3. Distribución de confianza ──────────────────────────────────
        rows3 = query(conn, "SELECT confidence FROM detections")
        confs = [r[0] for r in rows3]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(confs, bins=20, color="#55A868", edgecolor="white")
        ax.set_title("Distribucion de confianza de las detecciones", fontsize=14)
        ax.set_xlabel("Confianza del modelo")
        ax.set_ylabel("Número de detecciones")
        plt.tight_layout()
        fig.savefig(OUT_DIR / "distribucion_confianza.png", dpi=150)
        plt.close()
        print("Grafica 3: distribucion_confianza.png")

        # ── 4. Resumen en texto ───────────────────────────────────────────
        total_pages = query(conn, "SELECT COUNT(*) FROM pages")[0][0]
        total_det   = query(conn, "SELECT COUNT(*) FROM detections")[0][0]
        avg_conf    = query(conn, "SELECT AVG(confidence) FROM detections")[0][0]
        max_det     = query(conn, """
            SELECT COUNT(d.id), p.pub_date, p.lccn
            FROM pages p JOIN detections d ON d.page_id = p.id
            GROUP BY p.id ORDER BY COUNT(d.id) DESC LIMIT 1
        """)[0]

        print(f"\n=== Resumen ===")
        print(f"  Paginas en BD          : {total_pages}")
        print(f"  Detecciones totales    : {total_det}")
        print(f"  Confianza media        : {avg_conf:.3f}")
        print(f"  Pagina con mas vinetas : {max_det[0]} ({max_det[1]}, {max_det[2]})")
        print(f"\nGraficas guardadas en: {OUT_DIR}/")


if __name__ == "__main__":
    main()
