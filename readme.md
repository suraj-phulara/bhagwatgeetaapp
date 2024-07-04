
# Step-1: Create a model group wherein you will add your models
POST /_plugins/_ml/model_groups/_register
{
  "name": "remote_model_group",
  "description": "A model group for external models"
}

# Step-2: Below api would register the extrenal model to your model group created above
POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/all-distilroberta-v1",
  "version": "1.0.1",
  "model_group_id": "2MXLgI8BGsRvXcGy96Kf",
  "model_format": "TORCH_SCRIPT"
}

# Step-3: Below api call which allows to regsiter ML Model on data node
PUT _cluster/settings
{
  "persistent": {
    "plugins.ml_commons.only_run_on_ml_node": false
  }
}

# Step-4: This will show the status of model registration, status changes to 'COMPLETED'
GET /_plugins/_ml/tasks/UVFyGY8BEsBSD-YBht-d

# Note down the model ID returned from above .In my case it was - UlFyGY8BEsBSD-YBkd8d

# Step-5: Deploy the model
POST /_plugins/_ml/models/UlFyGY8BEsBSD-YBkd8d/_deploy

# This will also return task_id, keep it noted to check the status of deployment. In my case it was U1F5GY8BEsBSD-YBOd-Z


# Step -6 Test your model, for this use model_id you noted above.

POST /_plugins/_ml/_predict/text_embedding/UlFyGY8BEsBSD-YBkd8d
{
  "text_docs":[ "today is sunny"],
  "return_number": true,
  "target_response": ["sentence_embedding"]
}

# STEPS ON HOW TO CREATE VECTOR EMBEDDINGS ON OPENSEARCH

# STEP-1 : Create your ingest pipeline, note you will be using your model id here:
PUT /_ingest/pipeline/nlp-ingest-pipeline
{
  "description": "A text embedding pipeline",
  "processors": [
    {
      "text_embedding": {
        "model_id": "UlFyGY8BEsBSD-YBkd8d",
        "field_map": {
          "content": "vector_embedding"
        }
      }
    }
  ]
}

# STEP-2 :  Create mapping for your vector index
# Make use of "dynamic": "strict", to avoid new fields ingestion into our opensearch index

PUT /lth_vector_index
{
  "settings": {
    "index.knn": true,
    "default_pipeline": "nlp-ingest-pipeline"
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "long"
      },
      "vector_embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "engine": "lucene",
          "space_type": "l2",
          "name": "hnsw",
          "parameters": {}
        }
      },
      "content": {
        "type": "text",
        "index": false
      },
      "model":{
        "type": "keyword"
      }
    }
  }
}

# STEP-3: Move data from content index to lth_vector_index with reindexing
POST _reindex?wait_for_completion=false
{
  "source": {
    "index": "content",
    "_source": [
      "id",
      "content"
    ]
  },
  "dest": {
    "index": "lth_vector_index",
    "pipeline": "nlp-ingest-pipeline"
  }
}
# Make use of below APIS to check task status or cancel it

GET _tasks/YEav5IW4TRKTMnmPqaU4yg:20266
POST _tasks/YEav5IW4TRKTMnmPqaU4yg:20266/_cancel

# Now you can query your index like

GET /lth_vector_index/_search
{
  "_source": {
    "excludes": [
      "vector_embedding"
    ]
  },
  "query": {
    "bool": {
      "should": [
        {
          "script_score": {
            "query": {
              "neural": {
                "vector_embedding": {
                  "query_text": "What is smart drafting ?",
                  "model_id": "UlFyGY8BEsBSD-YBkd8d",
                  "k": 100
                }
              }
            },
            "script": {
              "source": "_score * 1.5"
            }
          }
        }
      ]
    }
  }
}
# To delete a deployed model follow below steps:
# 1) UNdeploy the model first with 
POST /_plugins/_ml/models/GIeUKI8BHB_SEELFt0LL/_undeploy
# the delete the model: 
DELETE /_plugins/_ml/models/GIeUKI8BHB_SEELFt0LL

# TO dump json docs to elastic index use below api
# curl -H 'Content-Type: application/x-ndjson' -XPOST 'localhost:9200/index-name/_bulk?pretty' --data-binary @reqs.json
# IMPORTANT LINKS
# 1) https://opensearch.org/docs/latest/clients/python-low-level/
