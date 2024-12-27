# llamacloud_streamlit
This repo uses Streamlit to create an user-facing demo application that showcases various capabilities from LlamaCloud.

You can use the application now by visiting https://example.com

You will need access to LlamaCloud in order to create an API key first to use within the app.

## Why did we create this?

We wanted to create a demo that showcases some of the Agentic RAG capabilities that LlamaCloud enables through an interactive UX.
Additionally, by open-sourcing the codebase for this, we hope that developers can use this code as a reference for setting up their own applications that rely on the LlamaCloud API.

## Development Setup

Here are the steps for setting up your development environment to run this project locally:

1. Clone this repo e.g. `gh repo clone run-llama/llamacloud_streamlit`
1. [Install `poetry`](https://python-poetry.org/docs/#installation) if you haven't already
1. Install the poetry dependencies by running `poetry shell` and then `poetry install` within this project's root directory.
1. Add a `secrets.toml` file in the `.streamlit` folder and add a value for `openai_key` to it
    - `touch .streamlit/secrets.toml`
    - Add a line within the newly created `secrets.toml` that reads `openai_key = "YOUR OPENAI API KEY"`
1. Run `make run` to run the streamlit app locally. You can then visit the application at `http://localhost:8501`
    - Please note you will need to setup the LlamaCloud API key the app will use on the API Keys tab in the UI first.



