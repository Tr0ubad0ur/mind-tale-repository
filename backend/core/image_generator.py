from typing import Optional

import torch
from diffusers import AutoPipelineForImage2Image, AutoPipelineForText2Image
from PIL import Image


class SD15Generator:
    """SD 1.5 генератор изображений.

    Поддерживает два режима:
    - text-to-image, если reference_image is None
    - image-to-image (img2img), если reference_image передан
    """

    _i2i = None
    _t2i = None

    def __init__(self, device: Optional[str] = None):
        """Создаёт генератор и настраивает устройство выполнения.

        Args:
            device: Явно заданное устройство ('mps', 'cuda', 'cpu'). Если None,
                выбирается автоматически (mps -> cuda -> cpu).
        """
        if device:
            self.device = device
        else:
            self.device = (
                'mps'
                if torch.backends.mps.is_available()
                else ('cuda' if torch.cuda.is_available() else 'cpu')
            )

        # На MPS float32 стабильнее, на CUDA можно float16
        self.dtype = (
            torch.float32
            if self.device == 'mps'
            else torch.float16
            if self.device == 'cuda'
            else torch.float32
        )

    def _load(self):
        if self.__class__._i2i is None:
            self.__class__._i2i = AutoPipelineForImage2Image.from_pretrained(
                'runwayml/stable-diffusion-v1-5',
                torch_dtype=self.dtype,
            ).to(self.device)
            self.__class__._i2i.enable_attention_slicing()

        if self.__class__._t2i is None:
            self.__class__._t2i = AutoPipelineForText2Image.from_pretrained(
                'runwayml/stable-diffusion-v1-5',
                torch_dtype=self.dtype,
            ).to(self.device)
            self.__class__._t2i.enable_attention_slicing()

    @torch.inference_mode()
    def generate(
        self,
        prompt: str,
        reference_image: Optional[Image.Image] = None,
        size: int = 512,
        strength: float = 0.65,
        steps: int = 25,
        guidance_scale: float = 7.0,
    ) -> Image.Image:
        """Генерирует изображение по тексту и (опционально) референсу.

        Args:
            prompt: Текстовый промпт.
            reference_image: Референс-картинка для img2img. Если None — используется text2img.
            size: Размер стороны изображения (size x size).
            strength: Сила изменения для img2img (чем выше, тем сильнее отличается от референса).
            steps: Количество шагов диффузии.
            guidance_scale: CFG scale.

        Returns:
            Сгенерированное изображение (PIL.Image) в RGB.
        """
        self._load()

        if reference_image is None:
            img = self.__class__._t2i(
                prompt=prompt,
                height=size,
                width=size,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
            ).images[0]
            return img.convert('RGB')

        ref = reference_image.convert('RGB').resize((size, size))
        img = self.__class__._i2i(
            prompt=prompt,
            image=ref,
            strength=strength,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
        ).images[0]
        return img.convert('RGB')
