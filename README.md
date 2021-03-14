# Braille Tiles Recognition

This repository is about automatic recognition of educational Braille Tiles with computer vision.

The primary goal is to develop a program for self-education of the visually impaired for studying Louis Braille's symbols system. The program will issue tasks - to assemble a word from tiles, and the trainee should compose this word and demonstrate it in front of the camera. The program will tell whether the answer is correct.

We plan to make this program a part of the educational Android app [Learn Braille](https://github.com/braille-systems/learn-braille).

You may find additional information about Braille Tiles in the [article](https://github.com/braille-systems/braille-trainer/wiki/tiles) (Russian).

# Распознавание плиток Брайля

Репозиторий содержит утилиту для распознавания обучающих плиток с символами Брайля по фотографии.

Конечная цель - создать программу для самостоятельного обучения незрячих чтению по системе Луи Брайля. Программа будет выдавать задания - выложить слово из плиток, а ученик должен составить это слово и продемонстрировать перед камерой. Программа скажет, верно или нет.

Мы планируем сделать эту программу частью обучающего Android-приложения [Learn Braille](https://github.com/braille-systems/learn-braille).

О плитках можно почитать в [статье](https://github.com/braille-systems/braille-trainer/wiki/tiles).

![result](https://user-images.githubusercontent.com/25281147/111088052-4195da00-8536-11eb-8b6d-84635c324fca.png)

## Датасет

Датасет можно скачать ![тут](https://disk.yandex.ru/d/vS5nZHeK9lezeQ?w=1). Архив нужно распаковать в корне проекта (рядом с `src` и `images` появится директория `data`).

Основные черты примеров:

- Разный фон на фотографии
- Перспективные искажения
- Различная освещенность
- Различные направления света + рассеянный свет (точки металлические и бликуют)
- Разные плитки
- Плитки комбинируются в слова, либо разбрасываются по изображению
- Плитки разложены под разными углами к горизонту камеры
- Различные фокус и резкость камеры

## Как запускать

```
$ cd tiles-recognition
$ pip install -r requirements.txt
$ python src/main.py
```

TODO

## Больше примеров работы

TODO
