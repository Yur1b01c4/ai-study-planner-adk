import datetime
import pytest
from app.agent import root_agent, app, get_instruction, FerramentasDeArquivo
from google.adk.tools.skill_toolset import SkillToolset


def test_agent_and_app_initialization():
    assert root_agent.name == "agente_estudos"
    assert app.name == "app"
    assert app.root_agent == root_agent


def test_instruction_provider_has_today_date():
    instruction = get_instruction()
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    assert hoje in instruction
    assert "Agente de Estudos" in instruction


@pytest.mark.asyncio
async def test_tools_configuration():
    tool_types = [type(t) for t in root_agent.tools]
    assert SkillToolset in tool_types
    assert FerramentasDeArquivo in tool_types

    file_toolset = next(t for t in root_agent.tools if isinstance(t, FerramentasDeArquivo))
    tools = await file_toolset.get_tools()
    tool_names = [t.name for t in tools]
    assert sorted(tool_names) == ["ReadFile", "WriteFile"]

    skill_toolset = next(t for t in root_agent.tools if isinstance(t, SkillToolset))
    skill_names = [s.name for s in skill_toolset.skills]
    assert "plano-de-estudos" in skill_names
