import asyncio

from dotenv import load_dotenv
import streamlit as st
from streamlit_code_diff import st_code_diff

from agent.schemas import ImplementationPlan, ReviewResult
from agent.state import AgentState
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from uuid import uuid4
import truststore

load_dotenv()
from agent.graph import get_graph


def app_main():
    truststore.inject_into_ssl()

    st.set_page_config(layout="wide")
    st.text_input("Enter project directory path", key="directory_path")
    st.text_input("Enter feature/bug request", key="user_request")
    graph = get_graph()
    if st.button("Send"):
        config: RunnableConfig = {"configurable": {"thread_id": str(uuid4())}}
        initial_state: AgentState = {
            "directory_path": st.session_state.directory_path,
            "user_request": st.session_state.user_request,
            "project_files": [],
            "retrieved_context": "",
            "retrieved_files": {},
            "analysis": "",
            "implementation_plan": ImplementationPlan(),
            "generated_changes": {},
            "review_result": ReviewResult(),
            "approved": False,
            "applied_files": [],
            "test_result": "",
            "retry_count": 0,
            "final_summary": "",
        }

        result = asyncio.run(graph.ainvoke(initial_state, config=config))
        st.session_state.agent_config = config
        st.session_state.agent_result = result
        st.session_state.agent_status = (
            "pending_approval" if "__interrupt__" in result else "completed"
        )

    if st.session_state.get("agent_status") == "pending_approval":
        result = st.session_state.agent_result
        payload = result["__interrupt__"][0].value

        # st.write("===== REVIEW =====")
        # review: ReviewResult = payload["review"]
        # st.write(f"AI review score: {review.review_score}")
        # st.write(f"AI review summary: {review.summary}")
        # st.write("AI review issues: ")
        # if len(review.issues) > 0:
        #     for index, issue in enumerate(review.issues):
        #         st.write(f"Issue {index}: {issue}")
        # else:
        #     st.write("No issues found.")

        st.title("Review changes and confirm")
        for file_path, diff in payload["diffs"].items():
            old_code = diff["original_content"]
            updated_code = diff["new_content"]
            st_code_diff(
                old_string=old_code,
                new_string=updated_code,
                language="python",
                key=file_path,
                filename=file_path,
            )

        approve_col, reject_col = st.columns(2)

        if approve_col.button("Approve"):
            resumed = asyncio.run(
                graph.ainvoke(
                    Command(resume=True),
                    config=st.session_state.agent_config,
                )
            )
            st.session_state.agent_result = resumed
            st.session_state.agent_status = (
                "pending_approval" if "__interrupt__" in resumed else "completed"
            )
            st.session_state.is_approved = True
            st.rerun()

        if reject_col.button("Reject"):
            resumed = asyncio.run(
                graph.ainvoke(
                    Command(resume=False),
                    config=st.session_state.agent_config,
                )
            )
            st.session_state.agent_result = resumed
            st.session_state.agent_status = (
                "pending_approval" if "__interrupt__" in resumed else "completed"
            )
            st.session_state.is_approved = False
            st.rerun()

    # if (
    #     st.session_state.get("agent_status") == "completed"
    #     and st.session_state.is_approved
    # ):
    #     result = st.session_state.agent_result
    #     st.write("\n===== ANALYSIS =====")
    #     st.write(result["analysis"])
    #     st.write("\n====================")

    #     st.write("\n===== PLAN =====")
    #     st.write(result["implementation_plan"])
    #     st.write("\n====================")

    #     st.write("\n===== GENERATED CHANGES =====")
    #     for file_path, value in result["generated_changes"].items():
    #         st.write(f"\n--- {file_path} ---")
    #         st.write(value.updated_content[:1000])
