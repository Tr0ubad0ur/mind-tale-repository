from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.image_style_rag import ImageStyleRAG
from backend.core.multimodal_rag import LocalRAG

router = APIRouter()
rag = LocalRAG()
image_rag = ImageStyleRAG()


class QueryRequest(BaseModel):
    """Schema for user query requests.

    Attributes:
        query (str): The text query from the user.
        top_k (int, optional): Number of top documents to retrieve from RAG. Defaults to 5.
        image (Optional[str], optional): Optional path or URL to an image to include in the query. Defaults to None.
    """

    query: str
    top_k: int = 5
    image: Optional[str] = None


@router.post('/ask')
def ask_mixed(request: QueryRequest) -> dict:
    """Handle a multimodal query request (text + optional image) and generate an answer using RAG.

    Args:
        request (QueryRequest): The query request containing the text, optional image, and retrieval parameters.

    Returns:
        dict: The generated answer from the RAG pipeline, potentially considering the image.
    """
    result = rag.generate_answer(
        request.query, top_k=request.top_k, image=request.image
    )
    return result


class ImageGenerateRequest(BaseModel):
    """Schema for user query requests.

    Attributes:
        user_id (str): The text query from the user.
        prompt (int, optional): Number of top documents to retrieve from RAG. Defaults to 5.
    """

    user_id: str
    prompt: str


@router.post('/generate_image')
def generate_image(request: ImageGenerateRequest) -> dict:
    """Generate an image for the given prompt.

    Implements "image-RAG" behavior: we search previous user prompts in Qdrant
    and, if a similar prompt exists, we use the previously generated image as a
    reference for a new generation (same style).
    """
    result = image_rag.generate(user_id=request.user_id, prompt=request.prompt)

    # Convert local filesystem path to a URL under /static
    # Example saved path: data/generated_images/<file>.png
    img_path = result.get('image_path', '')
    if img_path.startswith('data/'):
        result['image_url'] = '/static/' + img_path[len('data/') :]
    else:
        result['image_url'] = img_path

    ref = result.get('reference')
    if isinstance(ref, dict):
        ref_path = ref.get('image_path', '')
        if isinstance(ref_path, str) and ref_path.startswith('data/'):
            ref['image_url'] = '/static/' + ref_path[len('data/') :]
    return result


# TODO write this requests
# @router.post('/test_llm')
# @router.post('/test_qdrant')
