"""Materializa o plano sintético completo de Transportation."""

from src.analytics.transportation.planning import materializar_plano_completo


def main() -> None:
    """Materializa planned_trips para todo o demand_forecast."""
    quantidade_viagens = materializar_plano_completo()

    print(
        f"Plano de Transportation materializado com sucesso: "
        f"{quantidade_viagens} viagens."
    )


if __name__ == "__main__":
    main()