import os
import asyncio
from fastmcp import FastMCP, Context
from fastmcp.prompts.prompt import Message
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


GCP_PROJECT_ID = "delta-cosmos-460512-n8" # os.environ.get("GCP_PROJECT", "bigquery-101-401711")
GCP_LOCATION = "europe-west1" # os.environ.get("GCP_LOCATION", "us-west1")
BIGQUERY_TABLE_ID = f"{GCP_PROJECT_ID}.mcp_workshop.catalog" # os.environ.get("BIGQUERY_TABLE_ID", f"{GCP_PROJECT_ID}.mcp.hacker_news")
GEMINI_MODEL_ID = "gemini-2.0-flash" 


client = client = bigquery.Client(project=GCP_PROJECT_ID)


query = f"""
        SELECT 
            item_name,
            category,
            cost,
            description,
            stock_quantity,
            rating,
            supplier_id
        FROM `{BIGQUERY_TABLE_ID}`
        LIMIT 10 
    """


query_job = client.query(query)
# Format each row into a descriptive string
rows_formatted = []
for row in query_job:
    row_str = (
        f"- Item: {row.item_name}\n"
        f"  Category: {row.category}\n"
        f"  Cost: ${row.cost:.2f}\n" # Format cost as currency
        f"  Description: {row.description}\n"
        f"  Stock: {row.stock_quantity}\n"
        f"  Rating: {row.rating}/5.0\n"
        f"  Supplier ID: {row.supplier_id}\n"
        f"-----------------------------------"
    )
    rows_formatted.append(row_str)

context_data = "\n".join(rows_formatted)

prompt_str = f"""You are a helpful assistant.
Based ONLY on the following information from our knowledge base, answer the user's question.
If the information is not present in the provided context, clearly state that the information is not available.

Context from Knowledge Base:
---
{context_data}
---

User's Question: what is the cheperst product?

Answer:
"""


vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

model = GenerativeModel(GEMINI_MODEL_ID)
response = model.generate_content(
            prompt_str,
            generation_config={
                "max_output_tokens": 512,
                "temperature": 0.7,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )


if response.candidates and response.candidates[0].content.parts:
    print( response.candidates[0].content.parts[0].text)
elif hasattr(response, 'text') and response.text: # Fallback for simpler text responses
    print( response.text)