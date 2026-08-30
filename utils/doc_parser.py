"""GCS-to-GitHub Multimodal Hybrid PDF Document Parser Service."""

import io
import logging
import os
import re
from typing import List, Optional
import pymupdf
from google import genai
from google.cloud import storage
import pdfplumber
from utils.github_publisher import GitHubPublisherService

logger = logging.getLogger(__name__)


class PdfParserService:

  def __init__(
      self,
      gcs_bucket_name: str,
      github_token: Optional[str] = None,
      github_repo_name: Optional[str] = None,
      gcp_project_id: Optional[str] = None,
      gcp_location: str = "global",
      vision_model: str = "gemini-3.7-flash",
  ):
    token = github_token or os.getenv("GITHUB_TOKEN", "")
    repo_name = github_repo_name or os.getenv(
        "SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc"
    )

    self.bucket_name = gcs_bucket_name
    self.publisher = GitHubPublisherService(token, repo_name)
    self._gcs_client = None
    self._bucket = None
    self.vision_model = os.getenv("GEMINI_VISION_MODEL", vision_model)

    project_id = (
        gcp_project_id
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )
    location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GCP_LOCATION") or gcp_location

    if not project_id and not os.getenv("GEMINI_API_KEY"):
      try:
        import google.auth
        _, auth_project = google.auth.default()
        project_id = auth_project
      except Exception as auth_err:
        raise RuntimeError(
            f"Failed to detect Google Cloud credentials for Vertex AI GenAI client. "
            f"Please set GOOGLE_CLOUD_PROJECT. Details: {auth_err}"
        ) from auth_err

    if project_id:
      try:
        self.genai_client = genai.Client(
            vertexai=True, project=project_id, location=location
        )
        print(f"✓ Initialized Vertex AI GenAI client (project={project_id}, location={location}, model={self.vision_model})")
      except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Vertex AI GenAI client with project='{project_id}' and location='{location}': {e}"
        ) from e
    else:
      raise ValueError("Neither Google Cloud Project ID was provided.")

  @property
  def bucket(self):
    """Lazily loads the GCS bucket client with clear credential error handling."""
    if self._bucket is None:
      try:
        self._gcs_client = storage.Client()
        self._bucket = self._gcs_client.bucket(self.bucket_name)
      except Exception as e:
        raise RuntimeError(
            f"Failed to connect to GCS bucket '{self.bucket_name}'. "
            f"Google Cloud Application Default Credentials (ADC) were not found or lack permissions. "
            f"Error details: {e}"
        )
    return self._bucket

  def parse_pdf(self, pdf_bytes: bytes, source_filename: str) -> str:
    """Parses PDF bytes into structured LLM-ready Markdown."""
    markdown_sections: List[str] = [
        f"# Document Specification: `{source_filename}`\n",
        "> *Auto-parsed Multimodal PDF artifact for Agentic SDLC context"
        " grounding.*\n",
    ]

    pymupdf_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
      with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        previous_table_headers = None

        for page_idx, page in enumerate(pdf.pages):
          page_num = page_idx + 1
          page_lines: List[str] = [f"## Page {page_num}\n"]

          if page_idx < len(pymupdf_doc) and self.genai_client:
            pymupdf_page = pymupdf_doc[page_idx]
            images = pymupdf_page.get_images()
            drawings = pymupdf_page.get_drawings()
            has_visuals = bool(images) or (len(drawings) > 3)

            if has_visuals:
              diagram_summary = self._describe_page_diagrams(
                  pymupdf_page, page_num
              )
              if diagram_summary:
                page_lines.append(
                    f"### Page Diagrams & Flowcharts\n{diagram_summary}\n"
                )

          tables = page.extract_tables()
          for table in tables:
            table_md, current_headers = self._process_table(
                table, previous_table_headers
            )
            if table_md:
              page_lines.append(f"\n{table_md}\n")
              previous_table_headers = current_headers

          text = page.extract_text() or ""
          cleaned_text = self._clean_text_and_code(text)
          if cleaned_text:
            page_lines.append(cleaned_text)

          markdown_sections.append("\n".join(page_lines))
    finally:
      pymupdf_doc.close()

    full_markdown = "\n\n---\n\n".join(markdown_sections)
    return self._stitch_multipage_code_blocks(full_markdown)

  def _describe_page_diagrams(self, pymupdf_page, page_num: int) -> Optional[str]:
    if not self.genai_client:
      return None

    pix = pymupdf_page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")

    prompt = (
        "Examine this page image from an engineering technical specification document. "
        "If this page contains an architecture diagram, flowchart, sequence diagram, component model, or data flow, "
        "provide a comprehensive Markdown description of the architecture components, layers, connections, entities, and data flows. "
        "If there are NO diagrams or charts on this page, respond with exact text 'NO_DIAGRAMS'."
    )

    # Attempt with configured model, then fallback models
    candidate_models = [self.vision_model, "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.7-flash"]
    seen = set()
    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

    errors = []
    description = None
    for model_name in models_to_try:
      try:
        response = self.genai_client.models.generate_content(
            model=model_name,
            contents=[
                prompt,
                genai.types.Part.from_bytes(
                    data=img_bytes, mime_type="image/png"
                ),
            ],
        )
        description = response.text.strip() if response.text else None
        if description:
          print(f"Successfully extracted diagram description for Page {page_num} using model `{model_name}`")
          break
      except Exception as model_err:
        errors.append(f"{model_name}: {model_err}")
        print(f"Model `{model_name}` failed for Page {page_num}: {model_err}")
        continue

    if description is None and errors:
      raise RuntimeError(
          f"Vision model extraction failed for diagram on Page {page_num}. "
          f"Tried models: {'; '.join(errors)}"
      )

    if not description or "NO_DIAGRAMS" in description:
      return None
    return f"> **[Architecture Diagram & Component Flow - Page {page_num}]**:\n{description}"

  def _process_table(
      self, table: List[List[Optional[str]]], prev_headers: Optional[List[str]]
  ) -> tuple[Optional[str], Optional[List[str]]]:
    if not table or not table[0]:
      return None, prev_headers

    cleaned_rows = [
        [(cell.replace("\n", " ").strip() if cell else "") for cell in row]
        for row in table
    ]
    current_headers = cleaned_rows[0]
    is_repeated_header = prev_headers is not None and current_headers == prev_headers

    if is_repeated_header:
      body_rows = cleaned_rows[1:]
      if not body_rows:
        return None, prev_headers
      md_lines = ["| " + " | ".join(row) + " |" for row in body_rows]
      return "\n".join(md_lines), prev_headers

    body_rows = cleaned_rows[1:]
    md_lines = [
        "| " + " | ".join(current_headers) + " |",
        "| " + " | ".join(["---"] * len(current_headers)) + " |",
    ]
    for row in body_rows:
      md_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(md_lines), current_headers

  def _clean_text_and_code(self, text: str) -> str:
    text = re.sub(
        r"^(Page\s+\d+\s+of\s+\d+|Confidential|Internal Use Only)$",
        "",
        text,
        flags=re.M | re.I,
    )
    # Remove stray "None" artifacts from PDF export containers
    text = re.sub(r"^None\s*$", "", text, flags=re.M)
    text = re.sub(r"^(\d+\.[\d\.]*\s+[A-Z].*)$", r"### \1", text, flags=re.M)
    return text.strip()

  def _stitch_multipage_code_blocks(self, markdown_text: str) -> str:
    lines = markdown_text.split("\n")
    in_code_block = False
    fixed_lines = []
    for line in lines:
      if line.strip().startswith("```"):
        in_code_block = not in_code_block
      if in_code_block and line.strip() == "---":
        continue
      fixed_lines.append(line)
    if in_code_block:
      fixed_lines.append("```")
    return "\n".join(fixed_lines)

  def process_and_publish_document(
      self,
      gcs_blob_name: str,
      target_github_branch: str = "main",
      github_output_dir: str = "docs/",
  ) -> str:
    """Streams PDF from GCS, parses to Markdown, and commits to GitHub."""
    blob = self.bucket.blob(gcs_blob_name)
    if not blob.exists():
      raise FileNotFoundError(f"GCS Blob `{gcs_blob_name}` not found.")

    pdf_bytes = blob.download_as_bytes()
    filename = os.path.basename(gcs_blob_name)
    parsed_markdown = self.parse_pdf(pdf_bytes, filename)

    base_name = os.path.splitext(filename)[0]
    github_file_path = f"{github_output_dir.strip('/')}/{base_name}.md"
    commit_msg = (
        f"docs(parsed): auto-publish multimodal parsed MD for {filename} [skip"
        " ci]"
    )

    action = self.publisher.commit_file(
        file_path=github_file_path,
        content=parsed_markdown,
        commit_message=commit_msg,
        branch_name=target_github_branch,
    )
    return f"Successfully {action} `{github_file_path}` on branch `{target_github_branch}`."

  def process_and_publish_all_bucket_documents(
      self,
      prefix: str = "",
      target_github_branch: str = "main",
      github_output_dir: str = "docs/",
  ) -> List[str]:
    """Iterates through all PDF files in the GCS bucket, parses each to Markdown, and commits to GitHub."""
    blobs = list(self.bucket.list_blobs(prefix=prefix))
    pdf_blobs = [b for b in blobs if b.name.lower().endswith(".pdf")]

    if not pdf_blobs:
      msg = f"No PDF files found in GCS bucket `{self.bucket_name}`."
      logger.info(msg)
      return [msg]

    results = []
    for blob in pdf_blobs:
      try:
        res = self.process_and_publish_document(
            gcs_blob_name=blob.name,
            target_github_branch=target_github_branch,
            github_output_dir=github_output_dir,
        )
        results.append(res)
      except Exception as e:
        err_msg = f"Error parsing `{blob.name}`: {e}"
        logger.error(err_msg)
        results.append(err_msg)

    return results
