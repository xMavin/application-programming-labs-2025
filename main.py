import argparse
import sys
from image_analyzer import ImageAnalyzer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('annotation', help='Файл аннотации')
    parser.add_argument('--output-csv', default='result.csv')
    parser.add_argument('--output-plot', default='histogram.png')
    parser.add_argument('--sort-by', choices=['r', 'g', 'b'],
                        default='r')
    args = parser.parse_args()

    try:
        analyzer = ImageAnalyzer(args.annotation)
        df = analyzer.load_and_analyze()
        print(f"Обработано изображений: {len(df)}")

        print(f"Сортировка по каналу {args.sort_by}")
        df_sorted = analyzer.sort_by_channel(df, args.sort_by)

        print("Фильтрация (диапазон 200-255)")
        df_filtered = analyzer.filter_by_range(df_sorted, 200,
                                               255,
                                               args.sort_by)

        df_filtered.to_csv(args.output_csv, index=False, encoding='utf-8-sig')
        print(f"DataFrame сохранен: {args.output_csv}")


        analyzer.plot_histograms(df_sorted, args.output_plot)
        print(f"График сохранен: {args.output_plot}")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()