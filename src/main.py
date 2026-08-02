from src.database.create_tables import criar_tabelas
from src.etl.load_products import main as carregar_produtos
from src.etl.load_warehouses import main as carregar_depositos


def main() -> None:
    """
    Executa o pipeline inicial de criação e carga do banco de dados.
    """

    print("\n=== AI Supply Chain Copilot ===\n")

    criar_tabelas()
    carregar_produtos()
    carregar_depositos()

    print("\nPipeline ETL concluído com sucesso.\n")


if __name__ == "__main__":
    main()