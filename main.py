import os
import argparse
from utils import AutoClone, VectorDB, CodeQA
from typing import List
import deeplake
import logging

logger = logging.getLogger("deeplake")
logger.setLevel(logging.WARNING)


def main(args):
    if not args.chat_only:
        # Clone the repository and filter files
        auto_clone = AutoClone()
        auto_clone.clone_and_filter_files(args.repo, args.destination)

        # Create a vector store from the cloned repo
        source_dir = os.path.join(args.destination, auto_clone.repo_name)
        vector_db = VectorDB(source_dir)
        vector_db.create_vector_store(args.vector_db)

    # Configure the code question-answering system
    code_qa = CodeQA()
    code_qa.configure_retriever(args.vector_db)

    print("Enter your questions or type 'exit' to quit.")

    while True:
        user_input = input("question > ")
        if user_input.lower() == 'exit':
            break

        questions = [user_input]
        code_qa.chat(questions)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Code Question-Answering System')
    parser.add_argument('--repo', help='GitHub repository URL')
    parser.add_argument('--destination', help='Destination folder for the cloned repository')
    parser.add_argument('--vector-db', required=True, help='Path to the vector store')
    parser.add_argument('--chat-only', action='store_true', help='Use only the chat functionality with a pre-built vector store')

    args = parser.parse_args()

    if not args.chat_only and (args.repo is None or args.destination is None):
        parser.error("Both --repo and --destination arguments are required if not using --chat-only flag.")

    main(args)