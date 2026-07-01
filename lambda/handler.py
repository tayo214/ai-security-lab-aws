import json
import os
import boto3

# Initialize AWS clients
s3_client = boto3.client("s3")
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Environment variables set by Terraform
BUCKET_NAME = os.environ.get("KNOWLEDGE_BASE_BUCKET")
MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")


def get_knowledge_base_context(document_key: str) -> str:
    """
    Retrieve document content from S3 knowledge base.

    INTENTIONAL VULNERABILITY (Phase 1): No access controls on which
    documents can be retrieved. Any document key can be requested,
    enabling path traversal-style attacks in Phase 2.
    """
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=document_key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        return f"Error retrieving context: {str(e)}"


def invoke_bedrock(prompt: str) -> str:
    """
    Invoke Claude 3 Haiku via Bedrock.

    INTENTIONAL VULNERABILITY (Phase 1): No token limits enforced,
    no output validation. Raw model output returned directly.
    """
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = bedrock_client.invoke_model(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


def lambda_handler(event, context):
    """
    Main Lambda handler — RAG application entry point.

    INTENTIONAL VULNERABILITIES (Phase 1):
    1. No input validation — user input is passed directly into prompt
    2. No prompt template — raw concatenation enables prompt injection
    3. No output sanitization — model response returned unfiltered
    4. No authentication check — any caller can invoke this function
    5. Error messages expose internal details — information disclosure
    """
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        user_question = body.get("question", "")
        document_key = body.get(
            "document_key", "knowledge-base/company-faq.txt")

        # VULNERABILITY: No input validation
        # A hardened version would validate length, content, and structure
        if not user_question:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "question field is required"})
            }

        # Step 1: Retrieve context from S3
        context = get_knowledge_base_context(document_key)

        # VULNERABILITY: Raw string concatenation — no prompt template
        # This is the core prompt injection attack surface.
        # A hardened version would use a structured template with
        # clearly delimited user input that the model is instructed
        # to treat as data, not instructions.
        prompt = f"""You are a helpful customer service assistant.
Use the following document to answer the user's question.

Document:
{context}

User question: {user_question}

Answer:"""

        # Step 2: Invoke Bedrock
        answer = invoke_bedrock(prompt)

        # Step 3: Return response
        # VULNERABILITY: Raw model output with no filtering or validation
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "question": user_question,
                "answer": answer,
                "source_document": document_key
            })
        }

    except Exception as e:
        # VULNERABILITY: Exposes internal error details to caller
        # A hardened version returns a generic error message
        # and logs the detail internally only
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "type": type(e).__name__
            })
        }
