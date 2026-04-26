from dataclasses import dataclass
from datetime import date

@dataclass
class FechamentoDiario:
    data: date
    faturamento: float
    frequencia_alunos: int
    observacao: str = ""

@dataclass
class Despesa:
    data: date
    tipo: str
    categoria: str
    valor: float
    observacao: str = ""

    
