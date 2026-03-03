import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


class RAGEngine:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self._load_db()

    def _load_db(self):
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function
            )

    def ingest_file(self, file_path):
        """Loads a PDF, splits it, and adds to vector store."""
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)

        if self.vector_store is None:
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory
            )
        else:
            self.vector_store.add_documents(splits)

        return len(splits)

    def retrieve_context(self, query, k=4):
        """Searches the vector store for relevant content."""
        if not self.vector_store:
            return "No knowledge base loaded."

        results = self.vector_store.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results])

    def clear_db(self):
        """Clears the existing vector store."""
        if self.vector_store:
            self.vector_store.delete_collection()
            self.vector_store = None