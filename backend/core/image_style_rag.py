import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from PIL import Image

from backend.core.embeddings import text_embedding
from backend.core.image_generator import SD15Generator
from backend.utils.config_handler import Config
from backend.utils.image_storage import LocalImageStorage
from backend.utils.qdrant_handler import QdrantHandler


@dataclass
class ReferenceHit:
    """Результат поиска референса в истории пользователя.

    Attributes:
        score: Косинусная близость/оценка совпадения из векторного поиска.
        image_path: Путь к изображению, связанному с найденным запросом.
        generation_id: Идентификатор генерации (если нужен для логов/аналитики).
    """

    score: float
    image_path: str
    generation_id: str
    prompt: str


class ImageStyleRAG:
    """Image-RAG: retrieve previous user prompt + image and use it as a style reference.

    This class implements the exact logic you described:
      1) first generation -> save prompt embedding + image metadata into Qdrant
      2) next generation -> search in Qdrant by user_id for similar prompts
      3) if match score >= threshold -> load that image and pass as reference
    """

    def __init__(
        self,
        qdrant_url: str = Config.qdrant_url,
        image_size: int = Config.generation_image_size,
    ) -> None:
        """Инициализирует сервис image-RAG.

        Args:
            qdrant_url: URL Qdrant (например, 'http://localhost:6333').
            image_size: image_size.
        """
        self.history = QdrantHandler(
            url=qdrant_url,
            collection_name=Config.qdrant_user_history_collection,
            vector_size=Config.text_vector_size,
        )
        self.storage = LocalImageStorage(Config.images_dir)
        self.generator = SD15Generator()
        self.image_size = image_size

    def _retrieve_reference(
        self, user_id: str, prompt: str
    ) -> Optional[ReferenceHit]:
        vec = text_embedding(prompt)
        results = self.history.search(
            query_vector=vec,
            top_k=Config.user_history_top_k,
            user_id=user_id,
            score_threshold=0.0,
            with_payload=True,
            auto_enrich=False,
        )
        if not results:
            return None
        best = results[0]
        payload = best.get('payload') or {}
        img_path = payload.get('image_path')
        gen_id = payload.get('generation_id')
        prev_prompt = payload.get('prompt', '')
        if not img_path or not gen_id:
            return None
        return ReferenceHit(
            score=float(best.get('score', 0.0)),
            image_path=str(img_path),
            generation_id=str(gen_id),
            prompt=str(prev_prompt),
        )

    def generate(
        self,
        user_id: str,
        prompt: str,
    ) -> Dict[str, Any]:
        """Generate image for user prompt, optionally using a retrieved reference image."""
        ref = self._retrieve_reference(user_id=user_id, prompt=prompt)
        used_reference = False
        reference_image: Optional[Image.Image] = None
        reference_strength = 0.0

        if (
            ref is not None
            and ref.score >= Config.user_history_similarity_threshold
        ):
            try:
                reference_image = self.storage.load(ref.image_path)
                used_reference = True
                # map similarity -> img2img strength.
                # Higher similarity => lower strength (preserve style/composition more).
                thr = Config.user_history_similarity_threshold
                # normalize score to 0..1 above threshold
                t = (ref.score - thr) / max(1e-6, (1.0 - thr))
                # strength in [0.45..0.75]
                reference_strength = max(0.45, min(0.75, 0.75 - 0.30 * t))
            except Exception:
                reference_image = None
                used_reference = False

        img = self.generator.generate(
            prompt=prompt,
            reference_image=reference_image,
            size=self.image_size,
            strength=reference_strength if used_reference else 0.65,
        )

        image_path = self.storage.save_png(img)
        generation_id = str(uuid.uuid4())

        # Save to user history vector store
        vec = text_embedding(prompt)
        self.history.add_points(
            [
                {
                    'id': generation_id,
                    'vector': vec,
                    'payload': {
                        'user_id': user_id,
                        'generation_id': generation_id,
                        'prompt': prompt,
                        'image_path': image_path,
                    },
                }
            ]
        )

        return {
            'generation_id': generation_id,
            'image_path': image_path,
            'used_reference': used_reference,
            'reference': (
                {
                    'generation_id': ref.generation_id,
                    'image_path': ref.image_path,
                    'score': ref.score,
                    'prompt': ref.prompt,
                }
                if used_reference and ref is not None
                else None
            ),
        }
