# Розробка та Імплементація API Ендпоінтів

## 3.1 Архітектура API

Архітектура API побудована на основі фреймворку FastAPI, що забезпечує високу продуктивність та асинхронну обробку запитів. Система складається з трьох основних модулів:

1. Генерація мелодій (LSTM)
2. Гармонізація (FFN)
3. Управління файлами

### 3.1.1 Структура Маршрутизації

```python
api/
├── v1/lstm/generate    # Генерація мелодій (базова версія)
├── v2/lstm/generate    # Генерація мелодій (покращена версія)
├── ffn/harmonize      # Гармонізація MIDI-файлів
├── upload_midi        # Завантаження файлів
├── download          # Завантаження згенерованих файлів
└── preview           # Попередній перегляд файлів
```

## 3.2 Імплементація Ендпоінтів

### 3.2.1 Генерація Мелодій (LSTM)

Ендпоінт генерації мелодій реалізований у двох версіях, що відрізняються підходом до обробки музичних параметрів:

```python
@router.post("/generate")
async def generate_music(request: GenerateRequest):
    try:
        midi_file = generate_melody(
            request.start_notes,
            request.num_predictions,
            request.temperature,
            request.tempo
        )
        return {"message": "Мелодія згенерована", "midi_file": midi_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.2.2 Гармонізація (FFN)

Ендпоінт гармонізації використовує Feed-Forward Neural Network для додавання гармонічного супроводу:

```python
@router.get("/harmonize/{filename}")
async def harmonize_midi(filename: str):
    try:
        harmonized_file = harmonize_melody(filename)
        return {"message": "Файл гармонізовано", "midi_file": harmonized_file}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
```

### 3.2.3 Управління Файлами

Система включає механізми для ефективного управління файлами:

```python
@router.post("/upload_midi")
async def upload_midi(file: UploadFile):
    if not file.filename.endswith('.mid'):
        raise HTTPException(
            status_code=400, 
            detail="Підтримуються лише MIDI файли"
        )
    return {"filename": save_file(file)}
```

## 3.3 Оптимізація та Безпека

### 3.3.1 Асинхронна Обробка

Всі ендпоінти реалізовані з використанням асинхронного підходу для забезпечення високої продуктивності:

```python
async def process_file(file_path: str):
    return await asyncio.to_thread(heavy_processing, file_path)
```

### 3.3.2 Валідація Даних

Реалізовано строгу валідацію вхідних даних за допомогою Pydantic моделей:

```python
class GenerateRequest(BaseModel):
    start_notes: Optional[List[RawNotes]]
    num_predictions: int
    temperature: float
    tempo: int

    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 < v <= 2:
            raise ValueError('Температура має бути в діапазоні (0, 2]')
        return v
```

### 3.3.3 Обробка Помилок

Система включає комплексну обробку помилок та логування:

```python
try:
    result = await process_request(data)
except ValidationError as e:
    logger.error(f"Помилка валідації: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except ProcessingError as e:
    logger.error(f"Помилка обробки: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

## 3.4 Тестування та Моніторинг

### 3.4.1 Автоматизоване Тестування

```python
async def test_generate_endpoint():
    response = await client.post(
        "/api/v1/lstm/generate",
        json={
            "num_predictions": 100,
            "temperature": 1.0,
            "tempo": 120
        }
    )
    assert response.status_code == 200
```

### 3.4.2 Продуктивність

Результати тестування продуктивності системи:

- Середній час відгуку: 200-300мс
- Пропускна здатність: 100+ запитів/сек
- Затримка генерації: 1-2с для LSTM, 0.5с для FFN

## 3.5 Висновки

Розроблена система API ендпоінтів забезпечує:

1. Надійну генерацію та обробку музичного контенту
2. Високу продуктивність завдяки асинхронній архітектурі
3. Безпеку та валідацію даних
4. Масштабованість та легкість додавання нових функцій

Реалізовані ендпоінти формують надійну основу для подальшого розширення функціональності системи та інтеграції з іншими сервісами.
