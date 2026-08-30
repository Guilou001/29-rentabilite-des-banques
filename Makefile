# Prérequis : uv (https://docs.astral.sh/uv/)
UV ?= uv

setup:
	$(UV) sync --locked --all-extras

test:             ## 24 tests fermés, sans réseau ni gros fichiers
	$(UV) run pytest

lint:
	$(UV) run ruff check .

data:             ## les deux relevés du BSIF, 979 Mo, puis l'entrepôt DuckDB
	$(UV) run rdb fetch
	$(UV) run rdb entrepot

all:              ## tout : les identités, la décomposition, les contributions, les figures
	$(UV) run rdb tout
