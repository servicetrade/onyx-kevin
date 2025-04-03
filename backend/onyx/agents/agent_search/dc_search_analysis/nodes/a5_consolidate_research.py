from datetime import datetime
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter

from onyx.agents.agent_search.dc_search_analysis.states import MainState
from onyx.agents.agent_search.dc_search_analysis.states import ResearchUpdate
from onyx.agents.agent_search.models import GraphConfig
from onyx.agents.agent_search.shared_graph_utils.utils import write_custom_event
from onyx.chat.models import AgentAnswerPiece
from onyx.prompts.agents.dc_prompts import DC_FORMATTING_NO_BASE_DATA_PROMPT
from onyx.prompts.agents.dc_prompts import DC_FORMATTING_WITH_BASE_DATA_PROMPT
from onyx.utils.logger import setup_logger
from onyx.utils.threadpool_concurrency import run_with_timeout

logger = setup_logger()


def consolidate_research(
    state: MainState, config: RunnableConfig, writer: StreamWriter = lambda _: None
) -> ResearchUpdate:
    """
    LangGraph node to start the agentic search process.
    """
    datetime.now()

    graph_config = cast(GraphConfig, config["metadata"]["config"])
    graph_config.inputs.search_request.query

    search_tool = graph_config.tooling.search_tool

    write_custom_event(
        "initial_agent_answer",
        AgentAnswerPiece(
            answer_piece=" Generating the answer\n\n\n",
            level=0,
            level_question_num=0,
            answer_type="agent_level_answer",
        ),
        writer,
    )

    if search_tool is None or graph_config.inputs.search_request.persona is None:
        raise ValueError("search tool and persona must be provided for agentic search")

    # Populate prompt
    instructions = graph_config.inputs.search_request.persona.prompts[0].system_prompt

    agent_5_instructions = instructions.split("Agent Step 5:")[1].split("Agent End")[0]

    if "|Start Data|" and "|End Data|" in instructions:
        agent_5_base_data = instructions.split("|Start Data|")[1].split("|End Data|")[0]
    else:
        agent_5_base_data = None

    agent_5_task = agent_5_instructions.split("Task:")[1].split("Independent Sources:")[
        0
    ]
    agent_5_output_objective = agent_5_instructions.split("Output Objective:")[1]

    research_result_list = []

    if agent_5_task.strip() == "*concatenate*":
        object_research_results = state.object_research_results

        for object_research_result in object_research_results:
            object = object_research_result["object"]
            research_result = object_research_result["research_result"]
            research_result_list.append(f"Course: {object}\n\n{research_result}")

    research_results = "\n\n".join(research_result_list)

    # Create a prompt for the object consolidation

    if agent_5_base_data is None:
        dc_formatting_prompt = DC_FORMATTING_NO_BASE_DATA_PROMPT.format(
            text=research_results, format=agent_5_output_objective
        )
    else:
        dc_formatting_prompt = DC_FORMATTING_WITH_BASE_DATA_PROMPT.format(
            text=research_results, format=agent_5_output_objective
        )

    # Run LLM

    msg = [
        HumanMessage(
            content=dc_formatting_prompt,
        )
    ]

    dispatch_timings: list[float] = []

    fast_model = graph_config.tooling.fast_llm

    def stream_initial_answer() -> list[str]:
        response: list[str] = []
        for message in fast_model.stream(msg, timeout_override=30, max_tokens=None):
            # TODO: in principle, the answer here COULD contain images, but we don't support that yet
            content = message.content
            if not isinstance(content, str):
                raise ValueError(
                    f"Expected content to be a string, but got {type(content)}"
                )
            start_stream_token = datetime.now()

            write_custom_event(
                "initial_agent_answer",
                AgentAnswerPiece(
                    answer_piece=content,
                    level=0,
                    level_question_num=0,
                    answer_type="agent_level_answer",
                ),
                writer,
            )
            end_stream_token = datetime.now()
            dispatch_timings.append(
                (end_stream_token - start_stream_token).microseconds
            )
            response.append(content)
        return response

    try:
        _ = run_with_timeout(
            60,
            stream_initial_answer,
        )

    except Exception as e:
        raise ValueError(f"Error in consolidate_research: {e}")

    return ResearchUpdate(
        research_results=research_results,
        log_messages=["Agent Source Consilidation done"],
    )
