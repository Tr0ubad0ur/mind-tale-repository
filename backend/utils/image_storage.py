import hashlib
from pathlib import Path
from typing import Optional

from PIL import Image

from backend.utils.config_handler import Config


class LocalImageStorage:
    """Simple local image storage.

    Saves generated images to a folder on disk and returns a relative path
    that can be served by FastAPI as a static file.

    In production you would usually replace this with S3/MinIO and store the
    resulting URL in Postgres.
    """

    def __init__(self, images_dir: Optional[str] = None) -> None:
        """Создаёт хранилище изображений.

        Args:
            images_dir: Директория для сохранения изображений. Если None — берётся из конфигурации.
        """
        self.images_dir = Path(images_dir or Config.images_dir)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def _name_for(self, content: bytes, ext: str = 'png') -> str:
        sha = hashlib.sha256(content).hexdigest()
        return f'{sha[:32]}.{ext}'

    def save_png(self, img: Image.Image) -> str:
        """Save an image as PNG and return the relative path."""
        from io import BytesIO

        buff = BytesIO()
        img.save(buff, format='PNG')
        data = buff.getvalue()

        filename = self._name_for(data, ext='png')
        path = self.images_dir / filename
        path.write_bytes(data)

        # Return path relative to the backend project root
        return str(path)

    def load(self, path: str) -> Image.Image:
        """Загружает изображение из файла.

        Args:
            path: Путь к файлу изображения.

        Returns:
            PIL.Image в режиме RGB.
        """
        return Image.open(path).convert('RGB')
