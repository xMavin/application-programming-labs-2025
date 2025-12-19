import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QComboBox, QLineEdit, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from iterator import ImagePathIterator


class MainWindow(QMainWindow):
    """Главное окно приложения для просмотра датасета изображений."""

    def __init__(self) -> None:
        """Инициализация главного окна."""
        super().__init__()
        self.image_iterator: Optional[ImagePathIterator] = None
        self.current_image_path: Optional[str] = None
        self.init_ui()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Просмотр изображений")
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Режим:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Загрузить из папки")
        self.mode_combo.addItem("Загрузить из CSV")
        control_layout.addWidget(self.mode_combo)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Выберите папку или CSV файл")
        control_layout.addWidget(self.path_edit, stretch=1)

        self.load_button = QPushButton("Выбрать")
        self.load_button.clicked.connect(self.load_dataset)
        control_layout.addWidget(self.load_button)

        main_layout.addLayout(control_layout)

        self.info_label = QLabel("Выберите датасет для начала просмотра")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.info_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(500, 400)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        main_layout.addWidget(self.image_label, stretch=1)

        navigation_layout = QHBoxLayout()

        self.prev_button = QPushButton("Назад")
        self.prev_button.clicked.connect(self.show_previous_image)
        self.prev_button.setEnabled(False)
        navigation_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Вперед")
        self.next_button.clicked.connect(self.show_next_image)
        self.next_button.setEnabled(False)
        navigation_layout.addWidget(self.next_button)

        main_layout.addLayout(navigation_layout)

        self.statusBar().showMessage("Готово к работе")

    def load_dataset(self) -> None:
        """
        Загружает датасет из выбранной папки или CSV файла.
        """
        mode = self.mode_combo.currentIndex()

        try:
            if mode == 0:
                folder_path = QFileDialog.getExistingDirectory(
                    self,
                    "Выберите папку с изображениями",
                    "."
                )
                if folder_path:
                    self.path_edit.setText(folder_path)
                    self.image_iterator = ImagePathIterator(
                        folder_path=folder_path)
                    self.next_button.setEnabled(True)
                    self.prev_button.setEnabled(False)
                    self.show_next_image()

            elif mode == 1:
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Выберите CSV файл",
                    ".",
                    "CSV Files (*.csv);;All Files (*)"
                )
                if file_path:
                    self.path_edit.setText(file_path)
                    self.image_iterator = ImagePathIterator(
                        annotation_file=file_path)
                    self.next_button.setEnabled(True)
                    self.prev_button.setEnabled(False)
                    self.show_next_image()

        except ValueError as e:
            QMessageBox.warning(self, "Предупреждение", str(e))
            self.statusBar().showMessage("Ошибка: неверные параметры")

        except IOError as e:
            QMessageBox.critical(self, "Ошибка ввода/вывода", str(e))
            self.statusBar().showMessage("Ошибка чтения данных")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Неизвестная ошибка: {str(e)}")
            self.statusBar().showMessage("Ошибка загрузки датасета")

        finally:
            if (not self.image_iterator or
                    self.image_iterator.total_count() == 0):
                self.next_button.setEnabled(False)
                self.prev_button.setEnabled(False)
                self.info_label.setText(
                    "В выбранном датасете нет изображений")

    def show_next_image(self) -> None:
        """
        Отображает следующее изображение из датасета.
        """
        if not self.image_iterator:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Сначала выберите датасет (папку или CSV файл)"
            )
            return

        try:
            image_path = next(self.image_iterator)
            self.current_image_path = image_path
            self.display_image(image_path)
            self.update_image_info()
            self.update_navigation_buttons()


        except StopIteration:
            if self.image_iterator.total_count() == 0:
                QMessageBox.warning(
                    self,
                    "Нет изображений",
                    "Выбранный датасет не содержит изображений.\n"
                    "Убедитесь, что в папке есть файлы .jpg/.jpeg/.png "
                    "или CSV файл содержит правильные пути."
                )
                self.info_label.setText("Датасет не содержит изображений")
                self.statusBar().showMessage("Нет изображений")
            else:
                QMessageBox.information(
                    self,
                    "Информация",
                    "Достигнут конец датасета."
                )
                self.info_label.setText("Конец датасета")
                self.statusBar().showMessage("Конец датасета")
            self.next_button.setEnabled(False)
            self.prev_button.setEnabled(self.image_iterator.has_previous())

        except FileNotFoundError:
            error_msg = f"Файл не найден: {self.current_image_path}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            self.statusBar().showMessage("Файл не найден")
            if self.image_iterator.has_next():
                self.show_next_image()

        except Exception as e:
            error_msg = f"Не удалось загрузить изображение: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")
            if self.image_iterator.has_next():
                self.show_next_image()

    def show_previous_image(self) -> None:
        """
        Отображает предыдущее изображение из датасета.
        """
        if not self.image_iterator:
            return

        try:
            image_path = self.image_iterator.previous()

            if image_path:
                self.current_image_path = image_path
                self.display_image(image_path)
                self.update_image_info()
                self.update_navigation_buttons()
            else:
                self.prev_button.setEnabled(False)
                self.statusBar().showMessage("Начало датасета")

        except FileNotFoundError:
            error_msg = f"Файл не найден: {self.current_image_path}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            self.statusBar().showMessage("Файл не найден")

        except Exception as e:
            error_msg = f"Не удалось загрузить изображение: {str(e)}"
            QMessageBox.critical(self, "Ошибка", error_msg)
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")

    def update_image_info(self) -> None:
        """Обновляет информацию о текущем изображении."""
        if not self.image_iterator or not self.current_image_path:
            return

        current_idx = self.image_iterator.current_index()
        total = self.image_iterator.total_count()
        file_name = Path(self.current_image_path).name

        info_text = f"Изображение {current_idx} из {total}: {file_name}"
        self.info_label.setText(info_text)
        self.statusBar().showMessage(f"Загружено: {file_name}")

    def update_navigation_buttons(self) -> None:
        """Обновляет состояние кнопок навигации."""
        if not self.image_iterator:
            return

        self.prev_button.setEnabled(self.image_iterator.has_previous())
        self.next_button.setEnabled(self.image_iterator.has_next())

    def display_image(self, image_path: str) -> None:
        """
        Отображает изображение с сохранением пропорций.
        """
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                raise ValueError(
                    f"Не удалось загрузить изображение: {image_path}")

            original_width = pixmap.width()
            original_height = pixmap.height()

            if original_width <= 0 or original_height <= 0:
                raise ValueError("Некорректные размеры изображения")

            # Получаем размеры области отображения
            label_size = self.image_label.size()
            available_width = label_size.width()
            available_height = label_size.height()

            # Вычисляем масштаб с сохранением пропорций
            width_ratio = available_width / original_width
            height_ratio = available_height / original_height
            scale_ratio = min(width_ratio, height_ratio,
                              1.0)

            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)

            # Масштабируем с сохранением пропорций
            scaled_pixmap = pixmap.scaled(
                new_width,
                new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            raise Exception(f"Ошибка отображения изображения: {str(e)}")
