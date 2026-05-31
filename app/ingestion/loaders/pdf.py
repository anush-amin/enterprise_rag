import io
import logfire
from pypdf import PdfReader, PdfWriter
from google.cloud import documentai
from app.config import settings

MAX_PAGES_PER_REQUEST = 15
client = None

def initialize_document_ai_client():
    """Initialize Document AI client with Logfire error handling"""
    global client
    if client is not None:
        return client
    
    try:
        client = documentai.DocumentProcessorServiceClient()
        logfire.info("✅ Document AI client initialized successfully")
        return client
    except Exception as e:
        logfire.error(
            "❌ Failed to initialize Document AI client",
            exception=str(e),
            error_type=type(e).__name__,
            help_text="Ensure Google Cloud credentials are configured. See: https://cloud.google.com/docs/authentication/external/set-up-adc"
        )
        raise

def parse_pdf(file_path: str):
    """
    Parses PDF using Google Cloud Document AI.
    Automatically splits large PDFs into 15-page chunks to bypass synchronous API limits.
    """
    with logfire.span("📄 Document AI Parsing", filename=file_path):
        try:
            doc_client = initialize_document_ai_client()
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            logfire.info(f"Total pages: {total_pages}")

            name = doc_client.processor_path(
                settings.PROJECT_ID, 
                settings.GCP_DOC_AI_LOCATION, 
                settings.GCP_DOC_AI_PROCESSOR_ID
            )

            full_text = ""

            # If small enough, process entirely
            if total_pages <= MAX_PAGES_PER_REQUEST:
                with open(file_path, "rb") as f:
                    image_content = f.read()
                full_text = process_document_chunk(image_content, name, doc_client)
            else:
                # Split into chunks of MAX_PAGES_PER_REQUEST
                logfire.info(f"PDF exceeds {MAX_PAGES_PER_REQUEST} pages. Splitting into chunks...")
                
                for i in range(0, total_pages, MAX_PAGES_PER_REQUEST):
                    writer = PdfWriter()
                    chunk_end = min(i + MAX_PAGES_PER_REQUEST, total_pages)
                    
                    for page_num in range(i, chunk_end):
                        writer.add_page(reader.pages[page_num])
                    
                    # Write chunk to bytes
                    with io.BytesIO() as bytes_stream:
                        writer.write(bytes_stream)
                        chunk_bytes = bytes_stream.getvalue()
                        
                    with logfire.span(f"Processing pages {i+1} to {chunk_end}"):
                        chunk_text = process_document_chunk(chunk_bytes, name, doc_client)
                        full_text += chunk_text + "\n"

            if not full_text.strip():
                logfire.warning(f"⚠️ Document AI returned empty text for {file_path}")
            else:
                logfire.info(f"✅ Document AI successfully parsed {len(full_text)} characters")

            return full_text

        except Exception as e:
            logfire.error(
                "❌ Document AI Parse Failed",
                file_path=file_path,
                exception=str(e),
                error_type=type(e).__name__,
                traceback=True,
                help_text="Verify: 1) Processor ID is correct, 2) Document AI API is enabled, 3) Credentials are configured"
            )
            raise e


def process_document_chunk(image_content: bytes, name: str, doc_client) -> str:
    """Helper function to send a specific byte chunk to Document AI"""
    raw_document = documentai.RawDocument(
        content=image_content, 
        mime_type="application/pdf"
    )

    request = documentai.ProcessRequest(
        name=name, 
        raw_document=raw_document
    )

    result = doc_client.process_document(request=request)
    return result.document.text