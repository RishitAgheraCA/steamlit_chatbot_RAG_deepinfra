import psycopg2 as psycopg2
import os

from indexing.models import Indexing

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from openai import OpenAI


def create_new_embedding(content,doc_tag,project_name,file_name,last_commit_id):
    # Set up the OpenAI client with DeepInfra API
    openai = OpenAI(
        api_key="mYVTpJWjik3Fah3iSIzWBQcaIeBOJBx3",  # Replace with your actual API key
        base_url="https://api.deepinfra.com/v1/openai",
    )
    input = content

    embeddings = openai.embeddings.create(
        model="BAAI/bge-m3",
        input=input,
        encoding_format="float"
    )
    context_embedding = []
    if isinstance(input, str):
        print(embeddings.data[0].embedding)
        context_embedding = embeddings.data[0].embedding
    else:
        for i in range(len(input)):
            print(embeddings.data[i].embedding)
            context_embedding.append(embeddings.data[i].embedding)
    print(embeddings.usage.prompt_tokens)

    index = Indexing.objects.create(content=content, embedding=context_embedding, doc_tag=doc_tag, project_name=project_name, file_name=file_name, last_commit_id=last_commit_id)

    print("Document and embedding successfully inserted into the database.")
