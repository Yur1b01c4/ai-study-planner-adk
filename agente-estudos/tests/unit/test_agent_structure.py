import datetime
from pathlib import Path
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


@pytest.mark.asyncio
async def test_file_toolset_working_dir_and_write():
    file_toolset = next(t for t in root_agent.tools if isinstance(t, FerramentasDeArquivo))
    env = file_toolset._environment
    assert isinstance(env.working_dir, Path)
    assert env.working_dir.is_dir()

    tools = await file_toolset.get_tools()
    write_tool = next(t for t in tools if t.name == "WriteFile")
    read_tool = next(t for t in tools if t.name == "ReadFile")

    test_filename = "_test_sanity.txt"
    test_content = "teste de escrita"

    res_write = await write_tool.run_async(
        args={"path": test_filename, "content": test_content},
        tool_context=None,
    )
    assert res_write == {"status": "ok", "message": f"Wrote {test_filename}"}

    res_read = await read_tool.run_async(
        args={"path": test_filename},
        tool_context=None,
    )
    assert res_read["status"] == "ok"
    assert test_content in res_read["content"]

    test_file_path = env.working_dir / test_filename
    if test_file_path.exists():
        test_file_path.unlink()
