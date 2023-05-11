import os
import subprocess
from urllib.parse import urlparse
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from typing import List

load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['ACTIVELOOP_TOKEN'] = os.getenv('ACTIVELOOP_TOKEN')

class AutoClone:
    def __init__(self):
        """
        Initialize the automatic github clone class
        """
        self.repo_url = None
        self.allowed_extensions = None
        self.destination_folder = None
        
    def extract_repo_name(self, repo_url):
        """
        Extracts repo name from .git URL
        """
        path = urlparse(self.repo_url).path
        repo_name = os.path.splitext(os.path.basename(path))[0]
        return repo_name
    
    def clone_and_filter_files(self, repo_url, destination_folder):
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.jav', '.cpp']
        
        self.repo_url = repo_url
        self.destination_folder = destination_folder

        repo_name = self.extract_repo_name(self.repo_url)
        repo_destination_folder = os.path.join(self.destination_folder, repo_name)
        
        self.repo_destination_folder = repo_destination_folder
        self.repo_name = repo_name

        # Create the destination folder with the repo name if it doesn't exist
        os.makedirs(repo_destination_folder, exist_ok=True)

        # Clone the repo (without files)
        subprocess.run(['git', 'init', repo_destination_folder])
        subprocess.run(['git', 'remote', 'add', '-f', 'origin', repo_url], cwd=repo_destination_folder)
        subprocess.run(['git', 'config', 'core.sparseCheckout', 'true'], cwd=repo_destination_folder)

        # Create a .git/info/sparse-checkout file with the allowed extensions
        sparse_checkout_file = os.path.join(repo_destination_folder, '.git', 'info', 'sparse-checkout')
        with open(sparse_checkout_file, 'w') as f:
            for ext in self.allowed_extensions:
                f.write(f'*{ext}\n')

        # Pull the files
        subprocess.run(['git', 'pull', 'origin', 'HEAD'], cwd=repo_destination_folder)
        
        print('Execution successful \n repo: {} \n destination: {}'.format(repo_url, repo_destination_folder))

class VectorDB:
    def __init__(self, source_dir):
        self.source_dir = source_dir
        
    def load_documents_from_repo(self):

        docs = []
        
        for dirpath, dirnames, filenames in os.walk(self.source_dir):
            
            for file in filenames:

                try:
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    docs.extend(loader.load_and_split())
                except Exception as e:
                    pass

        self.docs = docs
        
    def split_docs(self):
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

        self.texts = text_splitter.split_documents(self.docs)
        
    def create_vector_store(self, dataset_path):
        embeddings = OpenAIEmbeddings()
        
        self.load_documents_from_repo()
        self.split_docs()

        self.db = DeepLake.from_documents(self.texts, embeddings, dataset_path=dataset_path)
        
        print('Execution successful. Vector store created. \n repo: {} \n destination: {}'.format(self.source_dir, dataset_path))

class CodeQA:
    def __init__(self, embeddings=OpenAIEmbeddings()):
        self.embeddings = embeddings
        self.chat_history = []
        
    def load_vectordb(self, dataset_path):
        print(f"Loading dataset from: {dataset_path}")
        self.db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=self.embeddings)
        
    def configure_retriever(self, dataset_path):
        self.load_vectordb(dataset_path)
        
        self.retriever = self.db.as_retriever()
        self.retriever.search_kwargs['distance_metric'] = 'cos'
        self.retriever.search_kwargs['fetch_k'] = 100
        self.retriever.search_kwargs['maximal_marginal_relevance'] = True
        self.retriever.search_kwargs['k'] = 10
        
    def chat(self, questions: List[str]):
        model = ChatOpenAI(model_name='gpt-3.5-turbo') # 'ada' 'gpt-3.5-turbo' 'gpt-4',
        
        qa = ConversationalRetrievalChain.from_llm(model, retriever=self.retriever)
        
        for question in questions:  
            result = qa({"question": question, "chat_history": self.chat_history})
            self.chat_history.append((question, result['answer']))
            print(f"**Answer**: {result['answer']} \n")