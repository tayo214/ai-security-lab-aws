# Package the Lambda function code into a zip file
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../../lambda/handler.py"
  output_path = "${path.module}/../../lambda/handler.zip"
}

resource "aws_lambda_function" "rag_handler" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-rag-handler"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  # INTENTIONAL VULNERABILITY (Phase 1): Generous timeout and memory
  # gives an attacker more runway for abuse. Phase 3 tightens these.
  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      KNOWLEDGE_BASE_BUCKET = aws_s3_bucket.knowledge_base.id
      BEDROCK_MODEL_ID      = "anthropic.claude-3-haiku-20240307-v1:0"
    }
  }

  # INTENTIONAL VULNERABILITY (Phase 1): No reserved concurrency limit.
  # An attacker hammering the endpoint can spin up hundreds of concurrent
  # executions, each invoking Bedrock — a model stealing / DoS vector.
  # Phase 3 adds reserved_concurrent_executions = 5

  depends_on = [
    aws_iam_role_policy.lambda_bedrock,
    aws_iam_role_policy_attachment.lambda_basic
  ]
}

# Allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rag_handler.function_name
  principal     = "apigateway.amazonaws.com"
}