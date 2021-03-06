# Распознавание плиток Брайля

## Постановка задачи

Создать инструмент, детектирующий плитки Брайля и распознающий символы, на них изображенные.

По фотографии выделить bounding boxes плиток Брайля (координаты левого верхнего угла и размер минимального описывающего прямоугольника) и распознать символы, на них обозначенные.

Подробнее про плитки можно почитать [тут](https://github.com/braille-systems/braille-trainer/wiki/tiles).

Выглядят они следующим образом:

![tile](https://user-images.githubusercontent.com/23435506/73558793-f53c2780-4464-11ea-965e-adbd76a7a998.JPG)

Пример решения:

![result](https://user-images.githubusercontent.com/25281147/111088052-4195da00-8536-11eb-8b6d-84635c324fca.png)

## Датасет

Датасет можно скачать [тут](https://disk.yandex.ru/d/vS5nZHeK9lezeQ?w=1).

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

Несколько примеров:
![1](https://user-images.githubusercontent.com/25281147/112543634-15e0e280-8dc7-11eb-9d48-f822883d79a6.jpg)
![13](https://user-images.githubusercontent.com/25281147/112543647-1aa59680-8dc7-11eb-8a97-82ffeda6a0c9.jpg)
![46](https://user-images.githubusercontent.com/25281147/112543669-21340e00-8dc7-11eb-83ad-3089f0ce3570.jpg)
![22](https://user-images.githubusercontent.com/25281147/112543683-26915880-8dc7-11eb-8c6f-fe7b415ddc2d.jpg)

## Как запускать

```
$ cd tiles-recognition
$ pip install -r requirements.txt
$ python src/main.py -v /path/to/directory/with/images
```

* Ключ `-v` - сохранять промежуточные результаты.
* Путь к директории с картинками.

Интерпретация результатов:

1. Красными линиями показывается контур предполагаемой плитки.
2. Маркер Х говорит о том, что контур не был отсеян после перспективного преобразования плитки.
3. Зелёный контур показывает принятую и распознанную плитку. Под плиткой - её номер в порядке слева направо, классифицированная буква и последовательность распознанных точек (в попядке сверху вниз, слева направо, F - filled, E - empty).

## Реализация

Основная идея:

1. Найти многоугольники, напоминающие брайлевские плитки
2. Вырезать каждую плитку и исправить перспективные искажения
3. Классифицировать каждую плитку
4. TODO: распознать составленное слово

### Первая итерация

#### Детектирование многоугольников, похожих на плитки Брайля

1. Картинка переводится в черно-белый формат
2. Фильтр Гаусса для сглаживания: ![blurred](https://user-images.githubusercontent.com/25281147/112550545-97893e00-8dd0-11eb-84ed-883a690a1397.png)
3. Адаптивная бинаризация: ![binary](https://user-images.githubusercontent.com/25281147/112550668-c4d5ec00-8dd0-11eb-8e65-d20c0e809f91.png)
4. Морфологическое открытие для сглаживания граней: ![opening](https://user-images.githubusercontent.com/25281147/112550763-ef27a980-8dd0-11eb-9356-d70170e5acd1.png)
5. Выделяем многоугольники с определённым количеством углов из определённого диапазона площадей: ![contours](https://user-images.githubusercontent.com/25281147/112550904-239b6580-8dd1-11eb-81f2-c8ce38571a42.png)

#### Отделение плиток

1. По контурам плитки вырезаются
2. По координатам углов контуров находятся 5 углов, соответствующих углам плитки
3. Исправляются перспективные искажения по 4м точкам и плитки приводятся к одному размеру

![warped-(177, 123)](https://user-images.githubusercontent.com/25281147/112551169-9ad0f980-8dd1-11eb-8801-cf6b797a7eef.png)
![warped-(466, 120)](https://user-images.githubusercontent.com/25281147/112551190-a58b8e80-8dd1-11eb-8831-37c5c359995a.png)
...

#### Классификация плиток

1. Плитка бинаризуется: ![binary](https://user-images.githubusercontent.com/25281147/112551515-2ba7d500-8dd2-11eb-8b63-ae47c6ccaaf9.png)
2. Для устранения шумв применяется морфологические закрытие: ![closing](https://user-images.githubusercontent.com/25281147/112551558-3f533b80-8dd2-11eb-8a03-ec2a00629ad7.png)
3. Находятся bounding boxes всех оставшихся на плитке контуров: ![bbs](https://user-images.githubusercontent.com/25281147/112551631-5d20a080-8dd2-11eb-85ae-5ea6e2417002.png)
4. По тому, какие bounding box'ы попадают целиком в области, где должны быть точки, определяем, какие точки присутствуют и классифицируем букву

#### Анализ результатов

В ходе работы пайплайн не менялся.
Производился подбор гиперпараметров и выбор конкретных морфологических алгоритмов и алгоритмов бинаризации.

С хорошо освещёнными рассеянным светом примерами без перспективных искажений алгоритм справляется хорошо:

![result](https://user-images.githubusercontent.com/25281147/112552050-34e57180-8dd3-11eb-9157-e1dcdf1b1ea4.png)

![51](https://user-images.githubusercontent.com/25281147/112552599-264b8a00-8dd4-11eb-8763-8d719b082048.png)

При слабом освещении удовлетворительно срабатывает поиск плиток, но совершенно не работает классификация:
![38](https://user-images.githubusercontent.com/25281147/112552456-e7b5cf80-8dd3-11eb-906a-d44acf81c664.png)

При смещённом свете длинные тени от точек мешают классификации:
![23](https://user-images.githubusercontent.com/25281147/112552725-509d4780-8dd4-11eb-86df-af5713290fed.png)

Думаю, что алгоритм нахождения плиток в целом удачный, только следует лучше подобрать гиперпараметры.

Алгоритм классификации кажется очень неудачным.
Он не работает при смене освещённости, мешают длинные тени, либо в условиях малой контрастности морфологическое преобразование полностью стирает точки.

### Вторая итерация

* Логирование промежуточных результатов стало удобнее
* Улучшена детекция
  * Лучше подобраны параметры бинаризации
  * Подобран параметр погрешности выделений полигонов
  * Добавлена фильтрация по выпуклости для полигонов
  * Добавлена фильтрация дупликатов полигонов (когда несколько полигонов соответствуют одной плитке)
* Улучшена классификация
  * Лучше подобраны параметры бинаризации
  * Контуры точек фильтруются по размерам описывающего прямоугольника
  * Прямоугольник классифицируется как конкретная точка, когда его центр попадает в область

Надо сказать, что очень сильно помогли советы @adtsvetkov, во многом благодаря которым детекция плиток стала работать просто идеально.
Также были хорошие идеи по улучшению классификации, которые помогут в дальнейшем, если текущее качество не будет достаточным.

## Анализ результатов

Детекция плиток теперь работает отлично, даже в самых тяжёлых условиях:

![contours-44](https://user-images.githubusercontent.com/25281147/113506731-448d5480-954f-11eb-864c-d77d19eb879b.png)
![contours-5](https://user-images.githubusercontent.com/25281147/113506741-4e16bc80-954f-11eb-859c-c7fcf198c46c.png)
![contours-33](https://user-images.githubusercontent.com/25281147/113506761-6d154e80-954f-11eb-8495-1026af62b979.png)

У классицикации всё ещё остаются сложности при освещении, выявляющем особенности фактуры поверхности плитки:

![bbs-13-4](https://user-images.githubusercontent.com/25281147/113506859-df862e80-954f-11eb-8e95-8014ea45a48d.png)

Но в целом точность стала удовлетворительной даже в не очень простых ситуациях:

![result-38](https://user-images.githubusercontent.com/25281147/113506894-1d835280-9550-11eb-952b-350cd7791406.png)
![result-32](https://user-images.githubusercontent.com/25281147/113506896-22480680-9550-11eb-9740-f61362265be0.png)
![result-6](https://user-images.githubusercontent.com/25281147/113506905-2a07ab00-9550-11eb-952a-b1f7d7486065.png)
