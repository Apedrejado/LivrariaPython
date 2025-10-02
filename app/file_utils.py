
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import csv
import os
from db import DB_PATH, get_connection
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "/backups"))
EXPORTS_DIR = Path(os.environ.get("EXPORTS_DIR", "/exports"))

def ensure_dirs():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

def backup_db(prefix: str = "backup_livraria") -> Path:
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = BACKUP_DIR / f"{prefix}_{timestamp}.db"
    src = Path(DB_PATH)
    if not src.exists():
        return dest
    shutil.copy2(src, dest)
    return dest

def cleanup_backups(keep: int = 5):
    ensure_dirs()
    files = sorted(BACKUP_DIR.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in files[keep:]:
        try:
            old.unlink()
        except Exception:
            pass

def export_csv(csv_filename: str = "livros_exportados.csv"):
    ensure_dirs()
    rows = []
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM livros ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    path = EXPORTS_DIR / csv_filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id","titulo","autor","ano_publicacao","preco"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return path

def import_csv(csv_path: str):
    conn = get_connection()
    cur = conn.cursor()
    imported = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            titulo = row.get("titulo") or row.get("titulo".lower())
            autor = row.get("autor") or row.get("autor".lower())
            try:
                ano = int(row.get("ano_publicacao") or 0) if row.get("ano_publicacao") else None
            except ValueError:
                ano = None
            try:
                preco = float(row.get("preco") or 0.0)
            except ValueError:
                preco = 0.0
            cur.execute(
                "INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
                (titulo, autor, ano, preco)
            )
            imported += 1
    conn.commit()
    conn.close()
    return imported

def gerar_relatorio_pdf(pdf_filename: str = "relatorio_livraria.pdf"):
    ensure_dirs()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM livros ORDER BY id")
    livros = [dict(r) for r in cur.fetchall()]
    conn.close()

    if not livros:
        return None 
    path = EXPORTS_DIR / pdf_filename
    c = canvas.Canvas(str(path), pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 2*cm, "Relatório de Livraria")
    c.setFont("Helvetica", 12)
    y = altura - 3*cm

    c.drawString(2*cm, y, "ID")
    c.drawString(4*cm, y, "Título")
    c.drawString(10*cm, y, "Autor")
    c.drawString(15*cm, y, "Ano")
    c.drawString(17*cm, y, "Preço")
    y -= 0.7*cm

    for livro in livros:
        c.drawString(2*cm, y, str(livro["id"]))
        c.drawString(4*cm, y, str(livro["titulo"]))
        c.drawString(10*cm, y, str(livro["autor"]))
        c.drawString(15*cm, y, str(livro["ano_publicacao"] or ""))
        c.drawString(17*cm, y, f"{livro['preco']:.2f}")
        y -= 0.7*cm
        if y < 2*cm: 
            c.showPage()
            y = altura - 2*cm

    c.save()
    return path
