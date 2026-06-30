resource "aws_s3_bucket" "knowledge_base" {
  bucket = "${var.project_name}-knowledge-base-${data.aws_caller_identity.current.account_id}"

  # INTENTIONAL VULNERABILITY (Phase 1): no versioning, no encryption,
  # no public access block, no logging. Documented in threat-model/threat_model.md
  # and remediated in Phase 3 hardening.
}

resource "aws_s3_object" "sample_doc" {
  bucket = aws_s3_bucket.knowledge_base.id
  key    = "knowledge-base/company-faq.txt"
  source = "${path.module}/../../lambda/sample-data/company-faq.txt"
  etag   = filemd5("${path.module}/../../lambda/sample-data/company-faq.txt")
}
