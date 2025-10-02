import click
import db
import repository
import file_utils
from tabulate import tabulate
import os

DB_PATH = os.environ.get("DB_PATH", "/data/livraria.db")

@click.group()
def cli():
    db.init_db()
    file_utils.ensure_dirs()

@cli.command()
@click.option("--titulo", prompt="Título")
@click.option("--autor", prompt="Autor")
@click.option("--ano", prompt="Ano de publicação", default="", show_default=False)
@click.option("--preco", prompt="Preço", type=float)
def adicionar(titulo, autor, ano, preco):
    """Adicionar novo livro (faz backup automático antes)."""
    file_utils.backup_db()
    try:
        ano_int = int(ano) if ano else None
    except ValueError:
        ano_int = None
    id_ = repository.add_livro(titulo, autor, ano_int, preco)
    file_utils.cleanup_backups(keep=5)
    click.echo(f"Livro adicionado com id {id_}")

@cli.command()
def listar():
    rows = repository.list_livros()
    if not rows:
        click.echo("Nenhum livro cadastrado.")
        return
    print(tabulate(rows, headers="keys", tablefmt="grid"))

@cli.command()
@click.option("--id", prompt="ID do livro", type=int)
@click.option("--preco", prompt="Novo preço", type=float)
def atualizar_preco(id, preco):
    file_utils.backup_db()
    ok = repository.update_preco(id, preco)
    if ok:
        click.echo("Preço atualizado.")
    else:
        click.echo("Livro não encontrado.")
    file_utils.cleanup_backups(keep=5)

@cli.command()
@click.option("--id", prompt="ID do livro", type=int)
def remover(id):
    file_utils.backup_db()
    ok = repository.delete_livro(id)
    if ok:
        click.echo("Livro removido.")
    else:
        click.echo("Livro não encontrado.")
    file_utils.cleanup_backups(keep=5)

@cli.command()
@click.option("--autor", prompt="Autor (ou parte do nome)")
def buscar_autor(autor):
    rows = repository.buscar_por_autor(autor)
    if not rows:
        click.echo("Nenhum livro encontrado para esse autor.")
        return
    print(tabulate(rows, headers="keys", tablefmt="grid"))

@cli.command()
def exportar():
    path = file_utils.export_csv()
    click.echo(f"Exportado para {path}")

@cli.command()
@click.option("--caminho", prompt="Caminho do CSV para importar")
def importar(caminho):
    file_utils.backup_db()
    imported = file_utils.import_csv(caminho)
    click.echo(f"{imported} linhas importadas.")
    file_utils.cleanup_backups(keep=5)

@cli.command()
def backup():
    dest = file_utils.backup_db()
    click.echo(f"Backup salvo em {dest}")
    file_utils.cleanup_backups(keep=5)

@cli.command()
def limpar():
    """Apagar todos os registros de livros (backup automático antes)."""
    file_utils.backup_db()
    confirm = input("Tem certeza que deseja apagar todos os dados? (s/n): ").lower()
    if confirm == "s":
        repository.clear_livros()
        click.echo("Todos os livros foram removidos do banco de dados.")
        file_utils.cleanup_backups(keep=5)
    else:
        click.echo("Operação cancelada.")

@cli.command()
def pdf():
    """Gerar relatório em PDF da livraria."""
    path = file_utils.gerar_relatorio_pdf()
    if path:
        click.echo(f"Relatório gerado em {path}")
    else:
        click.echo("Não há livros para gerar relatório.")

@cli.command()
def menu():
    while True:
        print("""
1. Adicionar novo livro
2. Exibir todos os livros
3. Atualizar preço de um livro
4. Remover um livro
5. Buscar livros por autor
6. Exportar dados para CSV
7. Importar dados de CSV
8. Fazer backup do banco de dados
9. Sair
10. Limpar todos os dados
11. Gerar em pdf
""")
        opc = input("Escolha: ").strip()
        if opc == "1":
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano = input("Ano de publicação (opcional): ")
            preco = input("Preço: ")
            try:
                preco_f = float(preco)
            except ValueError:
                print("Preço inválido.")
                continue
            file_utils.backup_db()
            try:
                ano_int = int(ano) if ano else None
            except ValueError:
                ano_int = None
            repository.add_livro(titulo, autor, ano_int, preco_f)
            file_utils.cleanup_backups(keep=5)
            print("Adicionado.")
        elif opc == "2":
            ctx = repository.list_livros()
            if ctx:
                print(tabulate(ctx, headers="keys", tablefmt="grid"))
            else:
                print("Nenhum livro.")
        elif opc == "3":
            try:
                id_ = int(input("ID do livro: "))
                novo = float(input("Novo preço: "))
            except ValueError:
                print("Entrada inválida.")
                continue
            file_utils.backup_db()
            ok = repository.update_preco(id_, novo)
            file_utils.cleanup_backups(keep=5)
            print("Atualizado." if ok else "Não encontrado.")
        elif opc == "4":
            try:
                id_ = int(input("ID do livro: "))
            except ValueError:
                print("ID inválido.")
                continue
            file_utils.backup_db()
            ok = repository.delete_livro(id_)
            file_utils.cleanup_backups(keep=5)
            print("Removido." if ok else "Não encontrado.")
        elif opc == "5":
            autor = input("Autor (ou parte do nome): ")
            rows = repository.buscar_por_autor(autor)
            if rows:
                print(tabulate(rows, headers="keys", tablefmt="grid"))
            else:
                print("Nenhum resultado.")
        elif opc == "6":
            path = file_utils.export_csv()
            print("Exportado para", path)
        elif opc == "7":
            caminho = input("Caminho do CSV: ")
            file_utils.backup_db()
            imp = file_utils.import_csv(caminho)
            file_utils.cleanup_backups(keep=5)
            print(f"{imp} linhas importadas.")
        elif opc == "8":
            dest = file_utils.backup_db()
            file_utils.cleanup_backups(keep=5)
            print("Backup salvo em", dest)
        elif opc == "10":
            confirm = input("Tem certeza que deseja apagar todos os dados? (s/n): ").lower()
            if confirm == "s":
                file_utils.backup_db()
                repository.clear_livros()
                file_utils.cleanup_backups(keep=5)
                print("Todos os dados foram removidos.")
            else:
                print("Operação cancelada.")
        elif opc == "11":
            path = file_utils.gerar_relatorio_pdf()
            if path:
                print(f"Relatório gerado em {path}")
            else:
                print("Não há livros para gerar relatório.")
        elif opc == "9":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    cli()
