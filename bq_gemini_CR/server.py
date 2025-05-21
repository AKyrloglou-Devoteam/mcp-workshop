import os
from fastmcp import FastMCP, Context
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold

# --- Configuration ---
# These should be configured by participants or via environment variables
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT", "bigquery-101-401711")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-west1")
BIGQUERY_TABLE_ID = os.environ.get("BIGQUERY_TABLE_ID", f"{GCP_PROJECT_ID}.mcp.hacker_news")
GEMINI_MODEL_ID = "gemini-1.5-flash-latest" 


# --- Initialize Vertex AI (once) ---
try:
    vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
except Exception as e:
    print(f"Warning: Vertex AI failed to initialize. Ensure GCP_PROJECT and GCP_LOCATION are set. Error: {e}")

# --- fastMCP Server Setup ---
mcp = FastMCP(name="BigQueryGeminiWorkshopAgent")

# --- Helper Functions ---
def get_bigquery_client():
    try:
        client = bigquery.Client(project=GCP_PROJECT_ID)
        return client
    except Exception as e:
        print(f"Error initializing BigQuery client: {e}")
        return None

def fetch_data_from_bigquery_table(bq_client: bigquery.Client, table_id: str, ctx: Context) -> str:
    """
    Fetches data from the specified BigQuery table (expected to be the catalog data)
    and formats it as a string for context.
    """
    if not bq_client:
        ctx.error("BigQuery client not available in fetch_data_from_bigquery_table.")
        return "Error: BigQuery client not initialized."
    
    # Simplified query for the workshop - reads specific columns from the predefined table
    # Example: SELECT product_name, description FROM `your-project.your_dataset.your_table` LIMIT 5
    # Participants would adapt this to their workshop table schema.
    # For this generic example, let's assume a table with 'item_name' and 'item_description'.
    query = f"""
        SELECT 
            item_name,
            category,
            cost,
            description,
            stock_quantity,
            rating,
            supplier_id
        FROM `{table_id}`
        LIMIT 10 
    """
    ctx.info(f"Executing BigQuery query on {table_id}")
    try:
        query_job = bq_client.query(query)
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
        
        if not rows_formatted:
            if ctx:
                ctx.warning(f"No data returned from BigQuery table: {table_id}")
            return "No relevant data found in the knowledge base for this query."
        
        # Join all formatted rows into a single string, separated by a newline
        return "\n".join(rows_formatted)
    except Exception as e:
        ctx.error(f"Error querying BigQuery table {table_id}: {e}")
        return f"Error fetching data from BigQuery: {str(e)}"

@mcp.prompt()
def format_prompt_for_gemini(context_data: str, user_question: str, ctx: Context) -> str:
    """
    Formats the prompt for Gemini using the BigQuery context and user question.
    The fastMCP framework can make this prompt available as a resource,
    but here the tool will call it directly as a utility.
    """
    ctx.info("Formatting prompt for Gemini.")
    # This is a simple string prompt. For more complex interactions,
    # you might return a list of Message objects or a more structured prompt.
    prompt_str = f"""You are a helpful assistant.
Based ONLY on the following information from our knowledge base, answer the user's question.
If the information is not present in the provided context, clearly state that the information is not available.

Context from Knowledge Base:
---
{context_data}
---

User's Question: {user_question}

Answer:
"""
    return prompt_str

async def call_gemini_model_async(prompt_str: str, ctx: Context) -> str:
    ctx.info(f"Sending prompt to Gemini model: {GEMINI_MODEL_ID}")
    try:
        model = GenerativeModel(GEMINI_MODEL_ID)
        response = await model.generate_content_async(
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
        ctx.info("Received response from Gemini.")
        # Accessing text, handling potential lack of response or blocked content
        if response.candidates and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        elif hasattr(response, 'text') and response.text: # Fallback for simpler text responses
             return response.text
        else:
            ctx.warning(f"Gemini response was empty or blocked. Feedback: {response.prompt_feedback}")
            return "Gemini could not provide an answer, possibly due to safety filters or an empty response."
    except Exception as e:
        ctx.error(f"Error calling Gemini API: {e}")
        return f"Error communicating with Gemini: {str(e)}"

# --- fastMCP Tool Definition ---
@mcp.tool()
async def answer_question_with_bigquery_context(user_question: str, ctx: Context) -> str:
    """
    Answers a user's question by fetching relevant context from a predefined
    BigQuery table and then querying the Gemini LLM.
    """
    ctx.info(f"Tool 'answer_question_with_bigquery_context' received question: '{user_question}'")

    bq_client = get_bigquery_client()

    # 1. Fetch context from BigQuery
    # BIGQUERY_TABLE_ID is a global config for this workshop example
    bq_context_data = fetch_data_from_bigquery_table(bq_client, BIGQUERY_TABLE_ID, ctx)
    if "Error:" in bq_context_data or "No relevant data" in bq_context_data:
        return bq_context_data # Return error or no data message

    # 2. Format the prompt using the @mcp.prompt defined function (called as a utility here)
    final_prompt = format_prompt_for_gemini(bq_context_data, user_question, ctx)

    # 3. Call Gemini with the formatted prompt
    gemini_answer = await call_gemini_model_async(final_prompt, ctx)
    
    return gemini_answer