import csv
from pathlib import Path
from typing import Optional, List


class ImagePathIterator:
    """Итератор по путям к файлам изображений."""

    def __init__(self, annotation_file: Optional[str] = None,
                 folder_path: Optional[str] = None) -> None:
        """
        Инициализация итератора.
        """
        self.paths: List[str] = []
        self.index: int = 0

        if annotation_file:
            self._load_from_csv(annotation_file)
        elif folder_path:
            self._load_from_folder(folder_path)
        else:
            raise ValueError(
                "Необходимо указать либо annotation_file, либо folder_path")

    def _load_from_csv(self, annotation_file: str) -> None:
        """Загружает пути из CSV файла."""
        try:
            csv_dir = Path(annotation_file).parent

            with open(annotation_file, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if not row:
                        continue
                    if len(row) >= 2:
                        rel_path = csv_dir / "images" / row[1].strip()
                        if rel_path.exists():
                            self.paths.append(str(rel_path))
                            continue
                    if row[0].strip():
                        abs_path = Path(row[0].strip())
                        if abs_path.exists():
                            self.paths.append(str(abs_path))

        except Exception as e:
            raise IOError(f"Ошибка чтения CSV файла: {e}")

    def _load_from_folder(self, folder_path: str) -> None:
        """Загружает пути из папки."""
        try:
            folder = Path(folder_path)
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']:
                for img_path in folder.rglob(ext):
                    self.paths.append(str(img_path.absolute()))
        except Exception as e:
            raise IOError(f"Ошибка чтения папки: {e}")

    def __iter__(self) -> 'ImagePathIterator':
        """Возвращает итератор."""
        return self

    def __next__(self) -> str:
        """Возвращает следующий путь к изображению."""
        if self.index < len(self.paths):
            path = self.paths[self.index]
            self.index += 1
            return path
        else:
            raise StopIteration

    def previous(self) -> Optional[str]:
        """
        Возвращает предыдущий путь к изображению.
        """
        if self.index > 1:
            self.index -= 2
            path = self.paths[self.index]
            self.index += 1
            return path
        elif self.index == 1:
            self.index = 0
            return None
        return None

    def get_current(self) -> Optional[str]:
        """
        Возвращает текущий путь к изображению.
        """
        if 0 < self.index <= len(self.paths):
            return self.paths[self.index - 1]
        return None

    def reset(self) -> None:
        """Сбрасывает итератор в начало."""
        self.index = 0

    def has_next(self) -> bool:
        """Проверяет, есть ли следующее изображение."""
        return self.index < len(self.paths)

    def has_previous(self) -> bool:
        """Проверяет, есть ли предыдущее изображение."""
        return self.index > 1

    def current_index(self) -> int:
        """Возвращает текущий индекс (1-based)."""
        return self.index

    def total_count(self) -> int:
        """Возвращает общее количество изображений."""
        return len(self.paths)