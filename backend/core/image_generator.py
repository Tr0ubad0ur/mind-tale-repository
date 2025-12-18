import hashlib
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


def _avg_color(img: Image.Image) -> Tuple[int, int, int]:
    # Cheap average color: downscale to 1x1
    return img.resize((1, 1)).getpixel((0, 0))


def _color_from_text(text: str) -> Tuple[int, int, int]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # avoid too-dark background
    r = 60 + (h[0] % 160)
    g = 60 + (h[1] % 160)
    b = 60 + (h[2] % 160)
    return r, g, b


class StubImageGenerator:
    """Coursework-friendly image generator.

    Пока у тебя нет настоящей text2img модели/сервиса.
    Этот генератор делает картинку PIL и "имитирует" референс-генерацию:
    если есть reference image, он подхватывает её средний цвет ("стиль").

    Потом ты заменяешь only one method: `generate(...)`.
    """

    def __init__(self, size: Tuple[int, int] = (768, 768)) -> None:
        self.size = size

    def generate(
        self,
        prompt: str,
        reference_image: Optional[Image.Image] = None,
        reference_strength: float = 0.75,
    ) -> Image.Image:
        w, h = self.size

        base = Image.new("RGB", (w, h), _color_from_text(prompt))

        if reference_image is not None:
            ref_color = _avg_color(reference_image)
            # Blend background toward ref color by strength
            overlay = Image.new("RGB", (w, h), ref_color)
            base = Image.blend(base, overlay, alpha=max(0.0, min(1.0, reference_strength)))

        # Draw text (so you can visually see what prompt was used)
        draw = ImageDraw.Draw(base)
        text = prompt.strip().replace("\n", " ")
        if len(text) > 140:
            text = text[:137] + "..."

        # Default font (works without system fonts)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        pad = 18
        box_h = 110
        # semi-transparent box via an RGBA layer
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        ldraw.rectangle((pad, h - box_h - pad, w - pad, h - pad), fill=(0, 0, 0, 120))
        ldraw.text((pad * 2, h - box_h), text, fill=(255, 255, 255, 255), font=font)
        base = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
        return base
