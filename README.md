# Braille Tiles Recognition

A tool for optical recognition of educational Braille Tiles.

![result](https://user-images.githubusercontent.com/23435506/120752512-849e9280-c512-11eb-88dc-412e6445e7ea.png)


The primary goal of this project is to develop a program for self-education of the visually impaired for studying Louis Braille's symbols system.
The program will be able to issue tasks - to assemble a word or phrase from tiles, and the user should compose this word/phrase and demonstrate it in front of the camera.
The program would tell whether the answer is correct.

Implementations: OpenCV - [`master` branch](https://github.com/braille-systems/tiles-recognition), PyTorch/YOLOv3 - [`rcnn` branch](https://github.com/braille-systems/tiles-recognition/tree/rcnn).

[OpenCV implementation report (RU)](https://github.com/braille-systems/tiles-recognition/blob/master/docs/report.ru.md).

We plan to incorporate this program into our educational [Android app Learn Braille](https://github.com/braille-systems/learn-braille) and an eponymous [iOS app](https://github.com/braille-systems/learnbraille_ios).
By now we've developed a simple frontend in the form of a [Telegram bot](https://github.com/braille-systems/angela_braille_bot).

You may find additional information about Braille Tiles in the [article](https://github.com/braille-systems/braille-trainer/wiki/tiles) (Russian).

Further information about our Optical Braille Recognition research: [wiki pages](https://github.com/braille-systems/brl_ocr/wiki).

BibTeX citation:
```bibtex
@inproceedings{zuev2021,
    author = {V.A.Zuev and A.S. Stoyan},
    booktitle = {Mathematics and Mathematical Modeling: Proceedings of XV
      All-Russian Scientific and Innovative School for young researchers},
    editor = {A.G. Sirotkina},
    pagetotal = {351},
    location = {Sarov},
    pages = {145-146},
    publisher = {Intercontact LLC},
    title = {Recognizing Braille in photos},
    year = {2021},
    ISBN = {978-5-6044528-8-2}
}
```

# Распознавание плиток Брайля

Репозиторий содержит утилиту для распознавания обучающих плиток с символами Брайля по фотографии.

Конечная цель - создать программу для самостоятельного обучения незрячих чтению по системе Луи Брайля. Программа будет выдавать задания - выложить слово или фразу из плиток, а ученик должен составить это слово/фразу и продемонстрировать перед камерой. Программа скажет, верно или нет.

Реализации: OpenCV - [ветвь `master`](https://github.com/braille-systems/tiles-recognition), PyTorch/YOLOv3 - [ветвь `rcnn`](https://github.com/braille-systems/tiles-recognition/tree/rcnn).

[Отчёт по OpenCV реализации](https://github.com/braille-systems/tiles-recognition/blob/master/docs/report.ru.md).

Мы планируем сделать эту программу частью обучающего Android-приложения [Learn Braille](https://github.com/braille-systems/learn-braille), а также одноимённого [iOS-приложения](https://github.com/braille-systems/learnbraille_ios).
К настоящему моменту разработан простой интерфейс в форме [Telegram-бота](https://github.com/braille-systems/angela_braille_bot).

О плитках можно почитать в [статье](https://github.com/braille-systems/braille-trainer/wiki/tiles).

Больше информации о нашем исследовании: [вики-страницы](https://github.com/braille-systems/brl_ocr/wiki).

Цитата для вставки в BibTeX:
```bibtex
@inproceedings{zuev2021,
    author = {В.А. Зуев and А.С. Стоян},
    booktitle = {Математика и математическое моделирование: Сборник материалов XV
    Всероссийской молодёжной научно-инновационной школы.},
    editor = {А.Г. Сироткиной},
    pagetotal = {351},
    location = {Саров},
    pages = {145-146},
    publisher = {ООО <<Интерконтакт>>},
    title = {Распознавание символов Брайля на фотографиях},
    year = {2021},
    ISBN = {978-5-6044528-8-2}
}
```

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
4. TODO: распознать составленное слово (сейчас алгоритм составления слова крайне примитивный, если на фото несколько строк, может работать некорректно).
