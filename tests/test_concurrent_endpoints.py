import asyncio
import time
import httpx
import pytest


@pytest.mark.asyncio
async def test_concurrent_requests():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Відправляємо повільний запит
        slow_task = asyncio.create_task(
            client.post("http://localhost:8000/api/v2/lstm/generate", json={
                "start_notes": [
                    {
                        "pitch": 60.0,
                        "duration": 1.0,
                        "step": 1.0
                    },
                    {
                        "pitch": 62.0,
                        "duration": 1.0,
                        "step": 1.0
                    },
                    {
                        "pitch": 64.0,
                        "duration": 1.0,
                        "step": 1.0
                    },
                    {
                        "pitch": 65.0,
                        "duration": 1.0,
                        "step": 1.0
                    }
                ],
                "num_predictions": 100,
                "temperature": 1.0,
                "tempo": 135
            })
        )

        # Даємо час для запуску першого запиту
        await asyncio.sleep(0.8)

        # Фіксуємо час початку
        start_time = time.time()

        # Відправляємо швидкий запит під час обробки повільного
        fast_response = await client.get("http://localhost:8000/api/preview/output_20250424_140627.mid")

        # Фіксуємо час закінчення швидкого запиту
        fast_time = time.time() - start_time

        # Чекаємо на завершення повільного запиту
        slow_response = await slow_task

        # Фіксуємо загальний час
        total_time = time.time() - start_time

        print(f"Швидкий запит завершено за {fast_time:.2f} секунд")
        print(f"Повільний запит завершено за {total_time:.2f} секунд")

        # Якщо швидкий запит завершився значно швидше повільного,
        # значить блокування немає
        if fast_time < 1.0:
            print("Ендпоінти не блокують один одного")
        else:
            print("Виявлено блокування - швидкий запит чекав на повільний")

        return fast_time, total_time, fast_response, slow_response

# Запуск тестів
if __name__ == "__main__":
    asyncio.run(test_concurrent_requests())
