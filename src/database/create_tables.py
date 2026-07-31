from src.database.connection import conectar_banco


def criar_tabela_produtos(cursor):
    """
    Cria o cadastro mestre de produtos.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            sku TEXT PRIMARY KEY,
            descricao TEXT NOT NULL,
            grupo_gerencial TEXT NOT NULL,
            unidade_medida TEXT NOT NULL,
            peso_kg REAL NOT NULL
                CHECK (peso_kg >= 0)
        )
        """
    )


def criar_tabela_depositos(cursor):
    """
    Cria o cadastro mestre de depósitos.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS depositos (
            codigo_deposito TEXT PRIMARY KEY,
            descricao TEXT NOT NULL,
            cidade TEXT NOT NULL,
            uf TEXT NOT NULL
        )
        """
    )


def criar_tabela_parametros_estoque(cursor):
    """
    Cria os parâmetros de planejamento de cada SKU por depósito.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS parametros_estoque (
            sku TEXT NOT NULL,
            codigo_deposito TEXT NOT NULL,
            estoque_minimo INTEGER NOT NULL
                CHECK (estoque_minimo >= 0),
            estoque_maximo INTEGER NOT NULL
                CHECK (estoque_maximo >= estoque_minimo),
            ponto_ressuprimento INTEGER NOT NULL
                CHECK (ponto_ressuprimento >= 0),

            PRIMARY KEY (sku, codigo_deposito),

            FOREIGN KEY (sku)
                REFERENCES produtos (sku),

            FOREIGN KEY (codigo_deposito)
                REFERENCES depositos (codigo_deposito)
        )
        """
    )


def criar_tabela_movimentacoes_estoque(cursor):
    """
    Cria o histórico de entradas e saídas de estoque.
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            sku TEXT NOT NULL,
            codigo_deposito TEXT NOT NULL,
            tipo_movimentacao TEXT NOT NULL
                CHECK (tipo_movimentacao IN ('ENTRADA', 'SAIDA')),
            quantidade INTEGER NOT NULL
                CHECK (quantidade > 0),
            documento_referencia TEXT,

            FOREIGN KEY (sku)
                REFERENCES produtos (sku),

            FOREIGN KEY (codigo_deposito)
                REFERENCES depositos (codigo_deposito)
        )
        """
    )


def criar_tabelas():
    """
    Cria todas as tabelas do módulo de gestão de estoque.
    """

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        criar_tabela_produtos(cursor)
        criar_tabela_depositos(cursor)
        criar_tabela_parametros_estoque(cursor)
        criar_tabela_movimentacoes_estoque(cursor)

        conexao.commit()

        print("Tabelas de gestão de estoque criadas ou já existentes.")

    finally:
        conexao.close()


if __name__ == "__main__":
    criar_tabelas()