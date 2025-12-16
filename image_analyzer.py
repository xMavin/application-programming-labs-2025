import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os


class ImageAnalyzer:
    def __init__(self, annotation_file: str):
        self.annotation_file = annotation_file

    def load_and_analyze(self) -> pd.DataFrame:
        """Загружает аннотацию и добавляет колонки с диапазонами яркости."""
        df = self._load_annotation_csv()

        df = self._find_and_add_paths(df)

        df = self._calculate_ranges(df)

        df = self._create_categories(df)

        return df

    def _load_annotation_csv(self) -> pd.DataFrame:
        """Загружает CSV с аннотациями."""
        return pd.read_csv(
            self.annotation_file,
            header=None,
            names=['Абсолютный путь', 'Относительный путь'],
            encoding="utf-8-sig"
        )

    def _find_and_add_paths(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ищет файлы и добавляет колонку 'Путь'."""
        base_dir = os.path.dirname(self.annotation_file)
        found_paths = []

        for idx, row in df.iterrows():
            rel_path = row['Относительный путь']
            possible_paths = [
                os.path.join(base_dir, 'images', rel_path),
                os.path.join(base_dir, rel_path),
                row['Абсолютный путь']
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    found_paths.append(path)
                    break
            else:
                found_paths.append(None)

        df['Путь'] = found_paths
        df = df[df['Путь'].notna()].copy()
        return df

    def _calculate_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        """Вычисляет диапазоны для RGB каналов."""
        ranges_r, ranges_g, ranges_b = [], [], []

        for path in df['Путь']:
            range_r, range_g, range_b = self._process_single_image(path)
            ranges_r.append(range_r)
            ranges_g.append(range_g)
            ranges_b.append(range_b)

        df['Диапазон_R'] = ranges_r
        df['Диапазон_G'] = ranges_g
        df['Диапазон_B'] = ranges_b

        return df

    def _process_single_image(self, path: str) -> tuple:
        """Обрабатывает одно изображение и возвращает диапазоны."""
        try:
            image = cv2.imread(path)
            if image is None:
                return 0.0, 0.0, 0.0

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            range_r = np.max(image_rgb[:, :, 0]) - np.min(image_rgb[:, :, 0])
            range_g = np.max(image_rgb[:, :, 1]) - np.min(image_rgb[:, :, 1])
            range_b = np.max(image_rgb[:, :, 2]) - np.min(image_rgb[:, :, 2])

            return float(range_r), float(range_g), float(range_b)

        except Exception as e:
            print(f"Ошибка обработки {path}: {e}")
            return 0.0, 0.0, 0.0

    def _create_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Создаёт категории для диапазонов."""
        bins = [0, 100, 150, 200, 210, 220, 230, 240, 250, 256]
        labels = ['0-100', '101-150', '151-200', '201-210', '211-220',
                  '221-230', '231-240', '241-250', '251-255']

        df['Категория_R'] = pd.cut(df['Диапазон_R'], bins=bins, labels=labels)
        df['Категория_G'] = pd.cut(df['Диапазон_G'], bins=bins, labels=labels)
        df['Категория_B'] = pd.cut(df['Диапазон_B'], bins=bins, labels=labels)

        return df

    def sort_by_channel(self, df: pd.DataFrame, channel: str = 'r')\
            -> pd.DataFrame:
        """Сортировка по каналу."""
        channel_map = {'r': 'Диапазон_R', 'g': 'Диапазон_G', 'b': 'Диапазон_B'}
        return df.sort_values(by=channel_map[channel])

    def filter_by_range(self, df: pd.DataFrame, min_val: float, max_val: float,
                        channel: str = 'r') -> pd.DataFrame:
        """Фильтрация по диапазону."""
        channel_map = {'r': 'Диапазон_R', 'g': 'Диапазон_G', 'b': 'Диапазон_B'}
        col = channel_map[channel]
        return df[(df[col] >= min_val) & (df[col] <= max_val)].copy()

    def plot_histograms(self, df: pd.DataFrame, save_path: str = None):
        """Три гистограммы"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        all_categories = ['0-100', '101-150', '151-200', '201-210', '211-220',
                         '221-230', '231-240', '241-250', '251-255']

        for idx, (channel, color, title) in enumerate(zip(
            ['R', 'G', 'B'], ['red', 'green', 'blue'], ['Красный канал',
                                                        'Зелёный канал',
                                                        'Синий канал']
        )):

            counts = df[f'Категория_{channel}'].value_counts()

            full_counts = {cat: counts.get(cat, 0) for cat in all_categories}


            x_pos = range(len(all_categories))
            axes[idx].bar(x_pos, list(full_counts.values()), color=color,
                          alpha=0.7)
            axes[idx].set_title(title)
            axes[idx].set_xlabel('Диапазон яркости')
            axes[idx].set_ylabel('Количество файлов')
            axes[idx].set_xticks(x_pos)
            axes[idx].set_xticklabels(all_categories, rotation=45)

            for i, v in enumerate(full_counts.values()):
                if v > 0:
                    axes[idx].text(i, v + 0.1, str(v), ha='center')

        plt.suptitle('Распределение диапазонов яркости (max-min) по'
                     ' каналам RGB')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        plt.show()