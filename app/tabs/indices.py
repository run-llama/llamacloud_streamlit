from typing import List
import streamlit as st
from utils import get_llamacloud_client, get_project_selector
from llama_cloud.types import (
    PipelineCreate,
    PipelineFileCreate,
    File,
    PipelineTransformConfig_Auto,
    PipelineCreateEmbeddingConfig_OpenaiEmbedding,
    OpenAiEmbedding
)


async def indices_tab():
    client = get_llamacloud_client()
    if client is None:
        st.write("Fill the form on the API Key tab first.")
        return
    supported_extensions = await client.parsing.get_supported_file_extensions()
    selected_project = await get_project_selector(client, "indices")

    project_container = st.container(border=True, key="project_container_indices")
    project_container.header(selected_project.name)

    with project_container.form(key="create_pipeline_form"):
        pipeline_name = st.text_input("Index Name", key="pipeline_name")
        create_pipeline_button = st.form_submit_button(label="Create Index")
            
        if create_pipeline_button:
            if not pipeline_name:
                project_container.error("Pipeline name cannot be empty.")
            else:
                openai_embedding = OpenAiEmbedding(api_key=st.secrets.openai_key)
                embedding_config = PipelineCreateEmbeddingConfig_OpenaiEmbedding(type="OPENAI_EMBEDDING", component=openai_embedding)
                pipeline_payload = PipelineCreate(
                    name=pipeline_name,
                    transform_config=PipelineTransformConfig_Auto(mode="auto"),
                    embedding_config=embedding_config,
                )
                await client.pipelines.upsert_pipeline(project_id=selected_project.id, request=pipeline_payload)
                project_container.success(f"Pipeline {pipeline_name} created!")
    
    pipelines = await client.pipelines.search_pipelines(project_id=selected_project.id)
    project_container.write(f"Add files to indices:")
    file_types = [supported_extension.lower() for supported_extension in supported_extensions]
    for pipeline in pipelines:
        pipeline_files = await client.pipelines.list_pipeline_files(pipeline_id=pipeline.id)
        pipeline_container = project_container.container(border=True, key="add_files_pipeline_" + pipeline.id)
        pipeline_container.subheader(pipeline.name)
        pipeline_container.write(f"Index ID: {pipeline.id}")
        pipeline_container.write(f"Files in index: {len(pipeline_files)}")
        with pipeline_container.form(key=f"add_files_form_pipeline_{pipeline.id}"):
            uploaded_files = st.file_uploader("Upload Files", type=file_types, key="files_" + pipeline.id, accept_multiple_files=True)
            add_files_button = st.form_submit_button(label="Add Files")
            if not add_files_button:
                continue
            project_files: List[File] = []
            for idx, uploaded_file in enumerate(uploaded_files):
                project_file = await client.files.upload_file(project_id=pipeline.project_id, upload_file=uploaded_file)
                project_files.append(project_file)
                st.toast(f"{idx + 1}/{len(uploaded_files)}: File {uploaded_file.name} uploaded to project {selected_project.name}!")
            await client.pipelines.add_files_to_pipeline(
                pipeline_id=pipeline.id,
                request=[
                    PipelineFileCreate(file_id=project_file.id)
                    for project_file in project_files
                ]
            )
            st.toast(f"{len(uploaded_files)} Files added to pipeline {pipeline.name}!")
