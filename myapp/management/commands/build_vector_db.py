# myapp/management/commands/build_vector_db.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

class Command(BaseCommand):
    help = 'Construye la base de datos vectorial ChromaDB a partir de los documentos fuente.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando la construcción de la base de datos vectorial..."))

        SOURCE_DIR = os.path.join(settings.BASE_DIR, 'chatbot_docs', 'source')
        DB_DIR = os.path.join(settings.BASE_DIR, 'chatbot_docs', 'chroma_db')

        if not os.path.exists(SOURCE_DIR) or not os.listdir(SOURCE_DIR):
            self.stderr.write(self.style.ERROR(f"El directorio fuente '{SOURCE_DIR}' no existe o está vacío. Por favor, añade archivos de documentación (.txt, .md)."))
            return

        self.stdout.write(f"Cargando documentos desde: {SOURCE_DIR}")
        
        # Cargar todos los documentos de texto y markdown
        loader = DirectoryLoader(SOURCE_DIR, glob="**/*[.md,.txt]", loader_cls=TextLoader, show_progress=True)
        documents = loader.load()

        if not documents:
            self.stderr.write(self.style.ERROR("No se encontraron documentos para procesar."))
            return

        self.stdout.write(f"Se cargaron {len(documents)} documentos.")

        # Dividir los documentos en trozos más pequeños
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        self.stdout.write(f"Documentos divididos en {len(texts)} trozos.")

        # Crear los embeddings
        self.stdout.write("Creando embeddings con Google... (esto puede tardar un momento)")
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

            # Crear y persistir la base de datos Chroma
            self.stdout.write(f"Creando y guardando la base de datos en: {DB_DIR}")
            vector_store = Chroma.from_documents(texts, embeddings, persist_directory=DB_DIR)
            
            self.stdout.write(self.style.SUCCESS("¡Base de datos vectorial construida y guardada exitosamente!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocurrió un error durante la creación de la DB: {e}"))