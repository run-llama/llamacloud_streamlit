import pandas as pd
import streamlit as st
from utils import get_llamacloud_client, get_project_selector
from llama_cloud.types import RetrieverCreate, RetrieverPipeline



async def composite_retriever_tab():
    client = get_llamacloud_client()
    if client is None:
        st.write("Fill the form on the API Key tab first.")
        return
    selected_project = await get_project_selector(client, "composite_retriever")
    
    project_container = st.container(border=True, key="project_container_composite_retriever")
    project_container.header(selected_project.name)

    pipelines = await client.pipelines.search_pipelines(project_id=selected_project.id)
    pipelines = sorted(pipelines, key=lambda p: p.name)
    pipeline_name_to_pipeline = {p.name: p for p in pipelines}
    with project_container.form(key="create_composite_retriever_form"):
        composite_retriever_name = st.text_input("Composite Retriever Name", key="composite_retriever_name")
        # sub_indices: List[RetrieverPipeline] = []
        # for idx, sub_index in enumerate(sub_indices):
        #     sub_index_container = st.container(border=True, key=f"sub_index_{idx}")
        #     sub_index_container.write(f"Sub-Index {idx}")
        #     default_pipeline_idx = next((i for i, p in enumerate(pipelines) if p.id == sub_index.pipeline_id), 0)
        #     selected_pipeline = st.selectbox("Select Sub-Index", pipelines, key=f"sub_index_{idx}_selectbox", index=default_pipeline_idx, format_func=lambda p: p.name)
        #     sub_index.pipeline_id = selected_pipeline.id
        # add_sub_index = st.button("Add Sub-Index")
        retriever_pipelines_df = st.data_editor(
            pd.DataFrame([{"name": None, "description": None, "pipeline_name": ""}]),
            column_config={
                "name": st.column_config.TextColumn("Name", required=True),
                "description": st.column_config.TextColumn("Description", required=False),
                "pipeline_name": st.column_config.SelectboxColumn("Index", options=[p.name for p in pipelines], required=True),
            },
            num_rows="dynamic",
            hide_index=False,
            key="retriever_pipelines_df"
        )
        create_composite_retriever_button = st.form_submit_button(label="Upsert Composite Retriever")
            
        if create_composite_retriever_button:
            if not composite_retriever_name:
                project_container.error("Composite Retriever name cannot be empty.")
            else:
                retriever_pipelines = [
                    RetrieverPipeline(
                        name=row.name,
                        description=row.description,
                        pipeline_id=pipeline_name_to_pipeline[row.pipeline_name].id
                    )
                    for row in retriever_pipelines_df.itertuples()
                ]
                retriever_create_payload = RetrieverCreate(
                    name=composite_retriever_name,
                    pipelines=retriever_pipelines
                )
                await client.retrievers.upsert_retriever(project_id=selected_project.id, request=retriever_create_payload)
                project_container.success(f"Composite Retriever {composite_retriever_name} upserted!")
    
    retrievers = await client.retrievers.list_retrievers(project_id=selected_project.id)
    if not retrievers:
        project_container.write("No existing Composite Retrievers found.")
        return
    pipeline_id_to_pipeline = {p.id: p for p in pipelines}
    project_container.write(f"Composite Retrievers:")
    for retriever in retrievers:
        retriever_container = project_container.container(border=True, key="retriever_" + retriever.id)
        retriever_container.subheader(retriever.name)
        retriever_container.write(f"Retriever ID: {retriever.id}")
        retriever_container.write(f"Sub-Indices in Composite Retriever: {len(retriever.pipelines)}")
        for sub_index in retriever.pipelines:
            sub_index_container = retriever_container.container(border=True, key=f"sub_index_{sub_index.name}")
            sub_index_pipeline = pipeline_id_to_pipeline[sub_index.pipeline_id]
            sub_index_container.subheader(f"Sub-Index: {sub_index.name}")
            sub_index_container.write(f"Description: {sub_index.description}")
            sub_index_container.write(f"Pipeline: {sub_index_pipeline.name}")
        delete_button = retriever_container.button("Delete 🗑️", key="delete_retriever_" + retriever.id)
        if delete_button:
            await client.retrievers.delete_retriever(retriever_id=retriever.id)
            retrievers = await client.retrievers.list_retrievers(project_id=selected_project.id)
            project_container.success(f"Composite Retriever {retriever.name} deleted!")

    
