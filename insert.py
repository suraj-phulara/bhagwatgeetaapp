import pandas as pd
from opensearchpy import OpenSearch
import numpy as np

def create_index(client, index_name):
    index_mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "chapter": {"type": "integer"},
                "verse": {"type": "keyword"},
                "verse_text": {"type": "text"},
                "translation": {"type": "text"},
                "commentary": {"type": "text"}
            }
        }
    }
    
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=index_mapping)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")

def import_csv_to_opensearch(client, csv_file, index_name):
    df = pd.read_csv(csv_file)
    df = df.replace({np.nan: ''})  # Replace NaN values with empty string

    successful_inserts = 0
    for i, row in df.iterrows():
        doc = {
            "id": row['id'],
            "chapter": row['chapter'],
            "verse": row['verse'],
            "verse_text": row['verse_text'].strip(),
            "translation": row['translation'].strip(),
            "commentary": row['commentary'].strip() if row['commentary'] else row['translation'].strip()
        }

        try:
            response = client.index(
                index=index_name,
                body=doc,
                id=row['id']  # Use 'id' as the document _id
            )
            print(f"Document ID {row['id']} indexed successfully.")
            successful_inserts += 1
        except Exception as e:
            print(f"Error indexing document ID {row['id']}: {e}")

    print(f"Successfully inserted {successful_inserts} documents into '{index_name}'.")

if __name__ == "__main__":
    # OpenSearch connection details
    opensearch_host = 'localhost'
    opensearch_port = 9200
    opensearch_username = 'admin'  # Replace with your OpenSearch username if using authentication
    opensearch_password = 'admin@123'  # Replace with your OpenSearch password if using authentication

    # Initialize OpenSearch client
    client = OpenSearch(
        hosts=[{'host': opensearch_host, 'port': opensearch_port}],
        http_auth=(opensearch_username, opensearch_password),
        use_ssl=False
    )

    # Index name and CSV file path
    index_name = 'bhagavad_gita_index'  # Replace with your desired index name
    csv_file_path = 'gita_verses.csv'  # Replace with the path to your CSV file

    # Create index and import data
    create_index(client, index_name)
    import_csv_to_opensearch(client, csv_file_path, index_name)
