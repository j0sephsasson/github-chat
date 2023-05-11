# github-chat
The Code Question-Answering System is an innovative command-line tool that allows you to chat with any GitHub repository using OpenAI's ChatGPT and a modern vector database, DeepLake. With this tool, you can ask questions about a codebase, and it will search through the repository to provide helpful answers.

## Features

- Clone any GitHub repository and filter files based on allowed extensions.
- Create a vector store using OpenAI embeddings for efficient search.
- Chat with the codebase by asking questions and receiving relevant answers.
- Support for both one-time setup and chat-only mode.

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
export ACTIVELOOP_TOKEN=<YOUR_ACTIVELOOP_TOKEN>
```
To get your OpenAI API Key, sign up for an account at https://platform.openai.com and access your API key.

To get your ActiveLoop Token, create an account at https://app.activeloop.ai and obtain your key.

## Usage
To use the Code Question-Answering System, run the following command with the appropriate arguments:

```bash
python main.py --repo <URL> --destination <PATH> --vector-db 'hub://<USERNAME>/<NAME>'
```
- `<URL>` : The GitHub repository URL you want to chat with.
- `<PATH>` : The local destination folder where the cloned repository will be stored.
- `<USERNAME>` : Your DeepLake username
- `<NAME>` : Name of vector database (will create a new one with this name if it doesn't exist)

Alternatively, if you have a pre-built vector store, you can use the `--chat-only` flag:
```bash
python main.py --chat-only --vector-db 'hub://<USERNAME>/<NAME>'
```

## How It Works
1. The tool clones the specified GitHub repository and filters files based on allowed extensions.
2. A vector store is created from the cloned repo using OpenAI embeddings.
3. A conversational retrieval chain is set up using OpenAI's ChatGPT and DeepLake's efficient search mechanism.
4. You can chat with the codebase by asking questions, and the tool will provide relevant answers by searching through the repository.

## Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.