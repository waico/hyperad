# hyperad
**Программное решение для определения заданных сегментов аудитории в мобильной среде по косвенным данным**

Разработанное data science AdTech решение является дополнением платформы Hyper Tech. ❗️В условиях ограничений политики конфиденциальности и передачи данных («cookie less» и «post idfa») мобильных операционных систем решение на основе моделей ML позволяет решать следующие задачи:  
✅ Классифицировать пользователей на заданные сегменты  
✅ Определять интересы пользователей и атрибуты их поведения  
✅ Формировать новые уникальные аудиторные сегменты  
✅ Оценивать охват по предложенным сегментам

**Стек решения:** *приложение:* python, aiohttp, grpc, vue.js, elasticsearch, docker; *ds/ml часть:* python3, catboost, sklearn, и тд.

**Уникальность:** кроме основного заявленного функционала решение позволяет 🔝создавать доработанную сегментацию для маркетинговых кампаний, 🔝строить дашборды и аналитику по выделенным сегментам, 🔝осуществлять мониторинг деградации и дообучение ML моделей. 

**Сроки разработки:** 3 месяца (разработка пилотной версии) ➕ 6-12 месяцев (пилотные испытания и доработка) ➕ 3-6 месяцев (промышленной внедрение)

**Стоимость разработки:** 0,5 млн руб (разработка пилотной версии) ➕ 2 млн руб (пилотные испытания и доработка) ➕ 1 млн руб (промышленной внедрение)

**Демо:** Демо приложения доступно по адресу: https://hyperad.waico.ru/

# ML часть
## Задача 1
Подготовка данных:
- Очистка данных
- Генерация признаков  
Код для предобработки данных находится [здесь](https://github.com/waico/hyperad/blob/datascience/notebooks/code/Process_data.ipynb).

Построение моделей классификации:
- CatboostClassifier 5 Folds  
Код для обучения моделей находится [здесь](https://github.com/waico/hyperad/blob/datascience/notebooks/code/Segmentation_Model.ipynb).

## Задача 2
Подготовка данных:
- Очистка данных
- Генерация признаков
- Добавление результатов классификации
- Категоризация
- Подвыборка данных

Возможные подходы:
- Иерархическая
- ROCK
- K-Modes
- Latent Class Analysis
- Нейронные сети (Автоэнкодеры) -> классические алгоритмы кластеризации
- Расчет мер близости (MCA, Gower) -> классические алгоритмы кластеризации

Более подробно в [этом](https://github.com/waico/hyperad/blob/datascience/notebooks/code/Clustering%20research.ipynb) ноутбуке.

# Приложение
## Запуск решения в Docker
Для запуска решения с помощью Docker (необходим **Docker Compose**) достаточно ввести следующие команды:

```
git clone https://github.com/waico/hyperad.git
cd ./hyperad
docker-compose up -d --build
```
Решение будет доступно по адресу http://127.0.0.1:8010/

## Запуск решения локально

Решение разворачивается на любой OS, однако разработка и отладка проводилась на OS Windows 10.

Необходимое ПО для разработки и запуска решения.
1) Python 3.8.5 `https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe`

Выполните следующие команды для запуска решения:

```
git clone https://github.com/waico/hyperad.git
cd ./hyperad/src
python -m venv venv
.\venv\Scripts\activate
pip install -r .\requirements.txt
python .\app.py --host 127.0.0.1 --port 8010
```
Решение будет доступно по адресу http://127.0.0.1:8010/