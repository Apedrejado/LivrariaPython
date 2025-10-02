
from db import get_connection
from typing import List, Dict, Any, Optional

def add_livro(titulo: str, autor: str, ano_publicacao: Optional[int], preco: float) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
        (titulo, autor, ano_publicacao, preco)
    )
    conn.commit()
    last = cur.lastrowid
    conn.close()
    return last

def list_livros() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM livros ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def update_preco(livro_id: int, novo_preco: float) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE livros SET preco = ? WHERE id = ?", (novo_preco, livro_id))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

def delete_livro(livro_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

def buscar_por_autor(autor: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM livros WHERE autor LIKE ? ORDER BY id", (f"%{autor}%",))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def clear_livros():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM livros")
    conn.commit()
    conn.close()
    return True
