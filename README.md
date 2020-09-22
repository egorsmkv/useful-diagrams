# Полезные диаграммы

## Как создаётся веб-сайт

<img src="./images/how_website_is_creating.png" width="700">
 
### PostgreSQL схема

<img src="./images/db_schema.png" width="700">

- Генерация SQL-схемы:
 
```
python3 tools/plantuml2mysql.py src/db_schema.puml sampledb
```
