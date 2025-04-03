from datetime import datetime
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter

from onyx.agents.agent_search.dc_search_analysis.states import ObjectInformationInput
from onyx.agents.agent_search.dc_search_analysis.states import ObjectResearchUpdate
from onyx.agents.agent_search.models import GraphConfig
from onyx.prompts.agents.dc_prompts import DC_OBJECT_CONSOLIDATION_PROMPT
from onyx.utils.logger import setup_logger
from onyx.utils.threadpool_concurrency import run_with_timeout

logger = setup_logger()


def consolidate_object_research(
    state: ObjectInformationInput,
    config: RunnableConfig,
    writer: StreamWriter = lambda _: None,
) -> ObjectResearchUpdate:
    """
    LangGraph node to start the agentic search process.
    """
    datetime.now()

    graph_config = cast(GraphConfig, config["metadata"]["config"])
    graph_config.inputs.search_request.query
    search_tool = graph_config.tooling.search_tool

    if search_tool is None or graph_config.inputs.search_request.persona is None:
        raise ValueError("search tool and persona must be provided for agentic search")

    instructions = graph_config.inputs.search_request.persona.prompts[0].system_prompt

    agent_4_instructions = instructions.split("Agent Step 4:")[1].split(
        "Agent Step 5:"
    )[0]
    # agent_4_task = agent_4_instructions.split("Task:")[1].split("Independent Sources:")[
    #    0
    # ]
    agent_4_output_objective = agent_4_instructions.split("Output Objective:")[1]

    object_information = state.object_information

    object = object_information["object"]
    information = object_information["information"]

    # Create a prompt for the object consolidation

    dc_object_consolidation_prompt = DC_OBJECT_CONSOLIDATION_PROMPT.format(
        object=object,
        information=information,
        format=agent_4_output_objective,
    )

    # Run LLM

    msg = [
        HumanMessage(
            content=dc_object_consolidation_prompt,
        )
    ]
    graph_config.tooling.primary_llm
    fast_llm = graph_config.tooling.fast_llm
    # Grader
    try:
        llm_response = run_with_timeout(
            30,
            fast_llm.invoke,
            prompt=msg,
            timeout_override=30,
            max_tokens=300,
        )

        cleaned_response = str(llm_response.content).replace("```json\n", "")
        consolidated_information = cleaned_response.split("INFORMATION:")[1]

    except Exception as e:
        raise ValueError(f"Error in consolidate_object_research: {e}")

    object_research_results = {
        "object": object,
        "research_result": consolidated_information,
    }

    return ObjectResearchUpdate(
        object_research_results=[object_research_results],
        log_messages=["Agent Source Consilidation done"],
    )
