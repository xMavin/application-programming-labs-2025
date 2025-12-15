import cv2
import numpy as np
from typing import Tuple, Optional
from enum import Enum
import matplotlib.pyplot as plt


class BackgroundType(str, Enum):
    """Типы фона для круглого изображения."""
    BLACK = "black"
    WHITE = "white"
    TRANSPARENT = "transparent"


def load_image(path: str) -> Optional[np.ndarray]:
    """Загружает изображение из файла."""
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f"Не удалось загрузить: {path}")
    return image


def get_image_info(image: np.ndarray) -> Tuple[int, int]:
    """Возвращает ширину и высоту изображения."""
    height, width = image.shape[:2]
    return width, height


def make_circular(image: np.ndarray, bg_type: BackgroundType) -> np.ndarray:
    """
    Преобразует изображение в круглое.
    """
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    radius = min(width, height) // 2
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)

    if bg_type == BackgroundType.TRANSPARENT:
        if len(image.shape) == 2:
            result = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
        elif image.shape[2] == 3:
            result = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        else:
            result = image.copy()
        result[:, :, 3] = cv2.bitwise_and(result[:, :, 3], mask)
    else:
        bg_color = (0, 0, 0) if bg_type == BackgroundType.BLACK else (255, 255,
                                                                      255)
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        result = image.copy()
        for c in range(3):
            result[:, :, c] = np.where(mask > 0, result[:, :, c], bg_color[c])

    return result


def save_image(image: np.ndarray, path: str) -> bool:
    """Сохраняет изображение в файл."""
    return cv2.imwrite(path, image)


def display_images(original: np.ndarray, result: np.ndarray,
                   bg_type: str) -> None:
    """
    Отображает оригинальное и обработанное изображение.
    """

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    if len(original.shape) == 3:
        original_disp = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    else:
        original_disp = cv2.cvtColor(original, cv2.COLOR_GRAY2RGB)

    if len(result.shape) == 3:
        if result.shape[2] == 4:
            result_disp = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
        else:
            result_disp = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    else:
        result_disp = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

    ax1.imshow(original_disp)
    ax1.set_title(f"Оригинал ({original.shape[1]}x{original.shape[0]})")
    ax1.axis('off')

    ax2.imshow(result_disp)
    ax2.set_title(f"Круглое (фон: {bg_type})")
    ax2.axis('off')

    plt.tight_layout()
    plt.show()