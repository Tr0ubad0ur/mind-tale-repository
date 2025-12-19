from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from backend.core.image_style_rag import ImageStyleRAG

router = APIRouter()
image_rag = ImageStyleRAG()


class ImageGenerateRequest(BaseModel):
    """Schema for user query requests.

    Attributes:
        user_id (str): The text query from the user.
        prompt (int, optional): Number of top documents to retrieve from RAG. Defaults to 5.
    """

    user_id: str
    prompt: str


@router.post('/generate_image')
async def generate_image(request: ImageGenerateRequest) -> dict:
    """Generate an image for the given prompt.

    Implements "image-RAG" behavior: we search previous user prompts in Qdrant
    and, if a similar prompt exists, we use the previously generated image as a
    reference for a new generation (same style).
    """
    result = await run_in_threadpool(
        image_rag.generate, user_id=request.user_id, prompt=request.prompt
    )

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
