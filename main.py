import argparse
import sys
from image_utils import (
    load_image, get_image_info, make_circular,
    save_image, display_images, BackgroundType
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Создание круглого изображения")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("-b", "--background",
                        choices=["black", "white", "transparent"],
                        default="black")
    parser.add_argument("-s", "--show",
                        action="store_true",
                        default=True)
    return parser.parse_args()


def main():
    args = parse_args()

    image = load_image(args.input)
    if image is None:
        sys.exit(1)

    width, height = get_image_info(image)
    print(f"Изображение: {args.input}")
    print(f"Размер: {width}x{height}")
    print(f"Фон: {args.background}")

    result = make_circular(image, BackgroundType(args.background))

    if save_image(result, args.output):
        print(f"Сохранено: {args.output}")
    else:
        print("Ошибка сохранения")
        sys.exit(1)

    if args.show:
        display_images(image, result, args.background)


if __name__ == "__main__":
    main()