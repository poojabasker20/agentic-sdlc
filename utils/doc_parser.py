"""GCS-to-GitHub Multimodal Hybrid PDF Document Parser Service.

Handles multi-page tables, spatial layout order, code snippets, and
visual flowcharts/diagrams via Vertex AI Gemini Vision.
"""

import io
import logging
import os
import re
from typing import List, Optional
from google import genai
from google.cloud import storage
import pdfplumber
import pymupdf
from utils.github_publisher import GitHubPublisherService

logger = logging.getLogger(__name__)


class PdfParserService:
  """Multimodal PDF Parser handling multi-page tables, code snippets, and diagrams via Vertex AI."""

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
    location = (
        os.getenv("GOOGLE_CLOUD_LOCATION")
        or os.getenv("GCP_LOCATION")
        or gcp_location
    )

    if not project_id:
      try:
        import google.auth
        _, auth_project = google.auth.default()
        project_id = auth_project
      except Exception as auth_err:
        raise RuntimeError(
            "Failed to detect Google Cloud credentials for Vertex AI GenAI"
            " client. Please set GOOGLE_CLOUD_PROJECT. Details:"
            f" {auth_err}"
        ) from auth_err

    if project_id:
      try:
        self.genai_client = genai.Client(
            vertexai=True, project=project_id, location=location
        )
        logger.info(
            "Initialized Vertex AI GenAI client (project=%s, location=%s,"
            " model=%s)",
            project_id,
            location,
            self.vision_model,
        )
      except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Vertex AI GenAI client with project='{project_id}' and location='{location}': {e}"
        ) from e
    else:
      raise ValueError("No Google Cloud Project ID was provided.")

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
            "Google Cloud Application Default Credentials (ADC) were not found"
            f" or lack permissions. Error details: {e}"
        ) from e
    return self._bucket

  def parse_pdf(self, pdf_bytes: bytes, source_filename: str) -> str:
    """Parses PDF bytes into structured LLM-ready Markdown while preserving spatial layout order."""
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

          # Vision Diagram Extraction
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

          # Spatial Interleaved Text & Table Extraction
          found_table_objs = page.find_tables()

          if not found_table_objs:
            # No tables on page: extract text normally
            text = page.extract_text() or ""
            cleaned_text = self._clean_text_and_code(text)
            if cleaned_text:
              page_lines.append(cleaned_text)
          else:
            # Sort tables vertically by top coordinate (y0)
            sorted_tables = sorted(found_table_objs, key=lambda t: t.bbox[1])
            raw_tables = page.extract_tables()

            current_top = 0
            page_height = page.height

            for idx, t_obj in enumerate(sorted_tables):
              x0, top, x1, bottom = t_obj.bbox

              # Crop and extract text slice above current table
              if top > current_top + 5:
                slice_box = (0, current_top, page.width, top)
                try:
                  text_slice = page.crop(slice_box).extract_text() or ""
                  cleaned_slice = self._clean_text_and_code(text_slice)
                  if cleaned_slice:
                    page_lines.append(cleaned_slice)
                except Exception:
                  pass

              # Process and format table grid at its natural vertical position
              if idx < len(raw_tables):
                table_md, current_headers = self._process_table(
                    raw_tables[idx], previous_table_headers
                )
                if table_md:
                  page_lines.append(f"\n{table_md}\n")
                  previous_table_headers = current_headers

              current_top = max(current_top, bottom)

            # Crop and extract text slice below last table to page bottom
            if current_top < page_height - 5:
              slice_box = (0, current_top, page.width, page_height)
              try:
                text_slice = page.crop(slice_box).extract_text() or ""
                cleaned_slice = self._clean_text_and_code(text_slice)
                if cleaned_slice:
                  page_lines.append(cleaned_slice)
              except Exception:
                pass

          markdown_sections.append("\n".join(page_lines))
    finally:
      pymupdf_doc.close()

    full_markdown = "\n\n---\n\n".join(markdown_sections)
    return self._stitch_multipage_code_blocks(full_markdown)

  def _describe_page_diagrams(
      self, pymupdf_page, page_num: int
  ) -> Optional[str]:
    """Renders page image and uses Vertex AI Gemini Vision to describe diagrams/flowcharts."""
    if not self.genai_client:
      return None

    pix = pymupdf_page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")

    prompt = (
        "Examine this page image from an engineering technical specification"
        " document. If this page contains an architecture diagram, flowchart,"
        " sequence diagram, component model, or data flow, provide a"
        " comprehensive Markdown description of the architecture components,"
        " layers, connections, entities, and data flows. If there are NO"
        " diagrams or charts on this page, respond with exact text"
        " 'NO_DIAGRAMS'."
    )

    raw_models = [
        self.vision_model,
        "gemini-3.7-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    models_to_try = []
    for m in raw_models:
      if m not in models_to_try:
        models_to_try.append(m)

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
          logger.info(
              "Successfully extracted diagram description for Page %d using"
              " model `%s`",
              page_num,
              model_name,
          )
          break
      except Exception as model_err:
        errors.append(f"{model_name}: {model_err}")
        logger.debug(
            "Model `%s` failed for Page %d: %s", model_name, page_num, model_err
        )
        continue

    if description is None and errors:
      logger.warning(
          "Vision diagram extraction skipped on Page %d. Errors: %s",
          page_num,
          "; ".join(errors),
      )
      return None

    if not description or "NO_DIAGRAMS" in description:
      return None

    return (
        f"> **[Architecture Diagram & Component Flow - Page {page_num}]**:\n{description}"
    )

  def _process_table(
      self,
      table: List[List[Optional[str]]],
      prev_headers: Optional[List[str]],
  ) -> tuple[Optional[str], Optional[List[str]]]:
    """Stitches multi-page tables and formats clean Markdown grids with cell line-break preservation."""
    if not table or not table[0]:
      return None, prev_headers

    cleaned_rows = []
    for row in table:
      cleaned_row = []
      for cell in row:
        if cell:
          c = (
              cell.replace("|", "\\|")
              .replace("\r\n", "<br>")
              .replace("\n", "<br>")
              .strip()
          )
          cleaned_row.append(c)
        else:
          cleaned_row.append("")
      cleaned_rows.append(cleaned_row)

    current_headers = cleaned_rows[0]
    is_repeated_header = (
        prev_headers is not None and current_headers == prev_headers
    )

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
    """Strips running headers/footers, unwraps multiline titles, and standardizes section headings."""
    if not text:
      return ""

    # Strip page headers & footers
    text = re.sub(
        r"^(Page\s+\d+\s+of\s+\d+|Confidential|Internal Use Only)$",
        "",
        text,
        flags=re.M | re.I,
    )
    text = re.sub(r"^None\s*$", "", text, flags=re.M)

    # Join split multiline section titles (e.g., "5. Auditability...\nLogging")
    text = re.sub(
        r"^(\d+(?:\.\d+)*\s+[A-Z][^\n:]+)\n([A-Z][A-Za-z0-9\s&,/-]+)$",
        r"\1 \2",
        text,
        flags=re.M,
    )

    # Top-Level Section Headings: e.g., "1. Executive Summary..." -> ## 1. Executive Summary...
    text = re.sub(
        r"^(\d+\.\s+[A-Z][^\n:]+)$",
        r"## \1",
        text,
        flags=re.M,
    )

    # Sub-Level Section Headings: e.g., "2.1 Data Classification..." -> ### 2.1 Data Classification...
    text = re.sub(
        r"^(\d+\.\d+(?:\.\d+)?\s+[A-Z][^\n:]+)$",
        r"### \1",
        text,
        flags=re.M,
    )

    return text.strip()

  def _stitch_multipage_code_blocks(self, markdown_text: str) -> str:
    """Ensures code blocks (```) broken across page boundaries remain contiguous."""
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
      github_output_dir: str = "docs/parsed",
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
      github_output_dir: str = "docs/parsed",
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
