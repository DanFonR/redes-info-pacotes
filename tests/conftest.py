import os
import sys

# adiciona src/ ao path do Python, para o pytest parar de reclamar
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src"),
    ),
)
