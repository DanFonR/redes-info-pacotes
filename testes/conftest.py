import os
import sys

# adiciona src/ ao PATH do Python para evitar erros e avisos do pytest
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src"),
    ),
)
