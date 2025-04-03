from datetime import datetime
from typing import cast

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter

from onyx.agents.agent_search.dc_search_analysis.ops import research
from onyx.agents.agent_search.dc_search_analysis.states import ObjectSourceInput
from onyx.agents.agent_search.dc_search_analysis.states import (
    ObjectSourceResearchUpdate,
)
from onyx.agents.agent_search.models import GraphConfig
from onyx.prompts.agents.dc_prompts import DC_OBJECT_SOURCE_RESEARCH_PROMPT
from onyx.utils.logger import setup_logger
from onyx.utils.threadpool_concurrency import run_with_timeout

logger = setup_logger()


def research_object_source(
    state: ObjectSourceInput,
    config: RunnableConfig,
    writer: StreamWriter = lambda _: None,
) -> ObjectSourceResearchUpdate:
    """
    LangGraph node to start the agentic search process.
    """
    datetime.now()

    graph_config = cast(GraphConfig, config["metadata"]["config"])
    graph_config.inputs.search_request.query
    search_tool = graph_config.tooling.search_tool

    object, document_source = state.object_source_combination

    if search_tool is None or graph_config.inputs.search_request.persona is None:
        raise ValueError("search tool and persona must be provided for agentic search")

    try:
        instructions = graph_config.inputs.search_request.persona.prompts[
            0
        ].system_prompt

        agent_2_instructions = instructions.split("Agent Step 2:")[1].split(
            "Agent Step 3:"
        )[0]
        agent_2_task = agent_2_instructions.split("Task:")[1].split(
            "Independent Sources:"
        )[0]
        agent_2_output_objective = agent_2_instructions.split("Output Objective:")[1]
    except Exception:
        raise ValueError(
            "Agent 1 instructions not found or not formatted correctly: {e}"
        )

    # Populate prompt

    # Retrieve chunks for objects

    if document_source:
        retrieved_docs = research(object, search_tool, [document_source])
    else:
        retrieved_docs = research(object, search_tool)

    # Generate document text

    document_texts_list = []
    for doc_num, doc in enumerate(retrieved_docs):
        chunk_text = "Document " + str(doc_num) + ":\n" + doc.content
        document_texts_list.append(chunk_text)

    document_texts = "\n\n".join(document_texts_list)

    # Built prompt

    dc_object_source_research_prompt = (
        DC_OBJECT_SOURCE_RESEARCH_PROMPT.format(
            task=agent_2_task,
            document_text=document_texts,
            format=agent_2_output_objective,
        )
        .replace("---object---", object)
        .replace("---source---", document_source.value)
    )

    # Run LLM

    msg = [
        HumanMessage(
            content=dc_object_source_research_prompt,
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
        cleaned_response = cleaned_response.split("RESEARCH RESULTS:")[1]
        object_research_results = {
            "object": object,
            "source": document_source.value,
            "research_result": cleaned_response,
        }

    except Exception as e:
        raise ValueError(f"Error in research_object_source: {e}")

    return ObjectSourceResearchUpdate(
        object_source_research_results=[object_research_results],
        log_messages=[f"Agent Step 2 done - {object} - {document_source.value}"],
    )
