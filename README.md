# Braille Tiles Recognition

This repository is about automatic recognition of educational Braille Tiles with computer vision.

The primary goal is to develop a program for self-education of the visually impaired for studying Louis Braille's symbols system.
The program will issue tasks - to assemble a word from tiles, and the trainee should compose this word and demonstrate it in front of the camera.
The program will tell whether the answer is correct.

Implementations: OpenCV - [`master` branch](https://github.com/braille-systems/tiles-recognition), PyTorch/YOLOv3 - [`rcnn` branch](https://github.com/braille-systems/tiles-recognition/tree/rcnn).

[OpenCV report]() (RU).

We plan to make this program a part of the educational Android app [Learn Braille](https://github.com/braille-systems/learn-braille).

You may find additional information about Braille Tiles in the [article](https://github.com/braille-systems/braille-trainer/wiki/tiles) (Russian).

Further information about our Optical Braille Recognition research: [wiki pages](https://github.com/braille-systems/brl_ocr/wiki).

# Распознавание плиток Брайля

Репозиторий содержит утилиту для распознавания обучающих плиток с символами Брайля по фотографии.

Конечная цель - создать программу для самостоятельного обучения незрячих чтению по системе Луи Брайля. Программа будет выдавать задания - выложить слово из плиток, а ученик должен составить это слово и продемонстрировать перед камерой. Программа скажет, верно или нет.

Реализации: OpenCV - [ветвь `master`](https://github.com/braille-systems/tiles-recognition), PyTorch/YOLOv3 - [ветвь `rcnn`](https://github.com/braille-systems/tiles-recognition/tree/rcnn).

Мы планируем сделать эту программу частью обучающего Android-приложения [Learn Braille](https://github.com/braille-systems/learn-braille).

О плитках можно почитать в [статье](https://github.com/braille-systems/braille-trainer/wiki/tiles).

Больше информации о нашем исследовании: [вики-страницы](https://github.com/braille-systems/brl_ocr/wiki).

![result](https://user-images.githubusercontent.com/25281147/111088052-4195da00-8536-11eb-8b6d-84635c324fca.png)

## Как запускать

```
$ cd tiles-recognition
$ pip install -r requirements.txt
$ python src/main.py /path/to/directory/with/images
```

Красными линиями показывается контур предполагаемой плитки. Маркер Х говорит о том, что контур не был отсеян после перспективного преобразования плитки. Зелёный контур показывает принятую и распознанную плитку.

## Датасет

Датасет можно скачать [тут](https://disk.yandex.ru/d/vS5nZHeK9lezeQ?w=1). Архив нужно распаковать в корне проекта (рядом с `src` и `images` появится директория `data`).

Основные черты примеров:

- Разный фон на фотографии
- Перспективные искажения
- Различная освещенность
- Различные направления света + рассеянный свет (точки металлические и бликуют)
- Разные плитки
- Плитки комбинируются в слова, либо разбрасываются по изображению
- Плитки разложены под разными углами к горизонту камеры
- Различные фокус и резкость камеры
- Различное удаление от камеры

## Как запускать



## Больше примеров работы

<details>
  <summary>Картинки</summary>

С неискаженными, хорошо освещёнными картинками, алгоритм справляется хорошо.
![10](https://user-images.githubusercontent.com/25281147/111091618-93456100-8544-11eb-8101-84b994ba7c25.png)
![7](https://user-images.githubusercontent.com/25281147/111091604-8a548f80-8544-11eb-84b2-56dc62d3b829.png)

Потребуется как-то фильтровать контуры, чтобы несколько не приходилось на одину плитку.
![8](https://user-images.githubusercontent.com/25281147/111091608-8cb6e980-8544-11eb-92f2-c84de0b96116.png)
![9](https://user-images.githubusercontent.com/25281147/111091614-904a7080-8544-11eb-8420-cb23ef783908.png)
![3](https://user-images.githubusercontent.com/25281147/111091584-79a41980-8544-11eb-9ea9-508022651839.png)
![4](https://user-images.githubusercontent.com/25281147/111091587-7c067380-8544-11eb-9b52-29a564ecce57.png)
![5](https://user-images.githubusercontent.com/25281147/111091592-7f016400-8544-11eb-93f9-49980f84f78d.png)

Длинные тени приводят к тому, что точки выходят за рамки отведённого bounding box'a.
Нужно ослабить условия на добавление точки в шеститочие.
![6](https://user-images.githubusercontent.com/25281147/111091600-858fdb80-8544-11eb-82ca-2dc77c12642a.png)

С очень тёмными изображениями алгоритм справляется плохо.
Потребуется увеличить чувствительность бинаризации.
![1](https://user-images.githubusercontent.com/25281147/111091767-15ce2080-8545-11eb-913b-df3bf70d3e13.png)
![2](https://user-images.githubusercontent.com/25281147/111091771-18c91100-8545-11eb-8819-be9b8216ab9d.png)

</details>
