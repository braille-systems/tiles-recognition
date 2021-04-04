# Braille Tiles Recognition

This repository is about automatic recognition of educational Braille Tiles with computer vision.

The primary goal is to develop a program for self-education of the visually impaired for studying Louis Braille's symbols system.
The program will issue tasks - to assemble a word from tiles, and the trainee should compose this word and demonstrate it in front of the camera.
The program will tell whether the answer is correct.

Implementations: OpenCV - [`master` branch](https://github.com/braille-systems/tiles-recognition), PyTorch/YOLOv3 - [`rcnn` branch](https://github.com/braille-systems/tiles-recognition/tree/rcnn).

[OpenCV implementation report (RU)](https://github.com/braille-systems/tiles-recognition/blob/master/docs/report.ru.md).

We plan to make this program a part of the educational Android app [Learn Braille](https://github.com/braille-systems/learn-braille).

You may find additional information about Braille Tiles in the [article](https://github.com/braille-systems/braille-trainer/wiki/tiles) (Russian).

Further information about our Optical Braille Recognition research: [wiki pages](https://github.com/braille-systems/brl_ocr/wiki).

# Распознавание плиток Брайля

Репозиторий содержит утилиту для распознавания обучающих плиток с символами Брайля по фотографии.

Конечная цель - создать программу для самостоятельного обучения незрячих чтению по системе Луи Брайля. Программа будет выдавать задания - выложить слово из плиток, а ученик должен составить это слово и продемонстрировать перед камерой. Программа скажет, верно или нет.

Реализации: OpenCV - [ветвь `master`](https://github.com/braille-systems/tiles-recognition), PyTorch/YOLOv3 - [ветвь `rcnn`](https://github.com/braille-systems/tiles-recognition/tree/rcnn).

[Отчёт по OpenCV реализации](https://github.com/braille-systems/tiles-recognition/blob/master/docs/report.ru.md).

Мы планируем сделать эту программу частью обучающего Android-приложения [Learn Braille](https://github.com/braille-systems/learn-braille).

О плитках можно почитать в [статье](https://github.com/braille-systems/braille-trainer/wiki/tiles).

Больше информации о нашем исследовании: [вики-страницы](https://github.com/braille-systems/brl_ocr/wiki).

![result](https://user-images.githubusercontent.com/25281147/111088052-4195da00-8536-11eb-8b6d-84635c324fca.png)

## Как запускать

```
$ cd tiles-recognition
$ pip install -r requirements.txt
$ python src/main.py -v /path/to/directory/with/images
```

* Ключ `-v` - сохранять промежуточные результаты.
* Путь к директории с картинками.

Интерпретация результатов:
1. Зелёными линиями показывается контур предполагаемой плитки.
2. Маркер Х говорит о том, что контур не был отсеян после перспективного преобразования плитки.
3. Под плиткой - её номер в порядке слева направо, классифицированная буква и последовательность распознанных точек (в попядке сверху вниз, слева направо, F - filled, E - empty).

## Примерный алгоритм

1. Найти многоугольники, напоминающие брайлевские плитки
2. Вырезать каждую плитку и исправить перспективные искажения
3. Классифицировать каждую плитку
4. TODO: распознать составленное слово
