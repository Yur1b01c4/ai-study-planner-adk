import datetime
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.apps import App
from google.adk.environment import LocalEnvironment
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.environment import EnvironmentToolset
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

load_dotenv()

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
SKILL_DIR = CURRENT_DIR / "skills" / "plano-de-estudos"
PLANOS_DIR = PROJECT_DIR / "planos"
PLANOS_DIR.mkdir(parents=True, exist_ok=True)

MODEL = os.getenv("MODEL", "gemini-3.8-flash")


class FerramentasDeArquivo(EnvironmentToolset):
    """EnvironmentToolset restrito para expor apenas ReadFile e WriteFile."""

    async def get_tools(self, readonly_context=None):
        tools = await super().get_tools(readonly_context)
        return [t for t in tools if t.name in ("ReadFile", "WriteFile")]


def get_instruction(context: ReadonlyContext | None = None) -> str:
    hoje = datetime.date.today()
    dias = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    dia_semana = dias[hoje.weekday()]
    data_formatada = hoje.strftime("%d/%m/%Y")

    return f"""Você é o Agente de Estudos, um mentor especialista em planejar estudos.
Você ajuda o usuário a montar planos de estudos personalizados, com cronograma, revisão espaçada e exportação para o Google Agenda.

Data de hoje: {data_formatada} ({dia_semana}).
Use esta data para interpretar e calcular expressões e referências temporais como 'hoje', 'amanhã', 'segunda que vem', etc.

Siga sempre as diretrizes e regras das skills disponíveis."""


skill = load_skill_from_dir(SKILL_DIR)
skill_toolset = SkillToolset(skills=[skill])
file_toolset = FerramentasDeArquivo(
    environment=LocalEnvironment(working_dir=str(PLANOS_DIR))
)

root_agent = Agent(
    name="agente_estudos",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=get_instruction,
    tools=[skill_toolset, file_toolset],
)

app = App(
    root_agent=root_agent,
    name="app",
)
