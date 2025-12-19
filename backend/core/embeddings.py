from functools import lru_cache
from typing import List

from PIL import Image


@lru_cache(maxsize=1)
def _get_text_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            'sentence-transformers is not installed. Install it with: pip install sentence-transformers'
        ) from e
    return SentenceTransformer('all-MiniLM-L6-v2')


def text_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a given text string.

    Args:
        text (str): The input text to encode.

    Returns:
        List[float]: A list of floats representing the text embedding.

    Notes:
        - This embedding can be stored in a vector database like Qdrant.
        - Ensure the model used for text embeddings is compatible with your retrieval pipeline.
    """
    model = _get_text_model()
    vector = model.encode(
        text
    ).tolist()  # преобразуем в список float для Qdrant
    return vector


@lru_cache(maxsize=1)
def _get_clip_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            'sentence-transformers is not installed. Install it with: pip install sentence-transformers'
        ) from e
    return SentenceTransformer('clip-ViT-B-32')


def image_embedding_from_path(image_path: str) -> List[float]:
    """Generate an embedding vector for an image from a file path.

    Args:
        image_path (str): Path to the image file to encode.

    Returns:
        List[float]: A list of floats representing the image embedding.

    Notes:
        - The image is converted to RGB before encoding.
        - Uses a CLIP-based model ("clip-ViT-B-32") for generating visual embeddings.
        - Embeddings can be stored in Qdrant or compared with other image embeddings.
    """
    img = Image.open(image_path).convert('RGB')
    model = _get_clip_model()
    vector = model.encode(img, convert_to_numpy=True).tolist()
    return vector
