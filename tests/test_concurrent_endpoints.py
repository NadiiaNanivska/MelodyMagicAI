import asyncio
import time
import httpx
import pytest

@pytest.mark.asyncio
async def test_concurrent_requests(capsys):
    async with httpx.AsyncClient(timeout=60.0) as client:
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
        await asyncio.sleep(0.8)
        start_time = time.time()
        # Відправляємо швидкий запит під час обробки повільного
        fast_response = await client.get("http://localhost:8000/api/preview/output_20250424_140627.mid")
        # Фіксуємо час закінчення швидкого запиту
        fast_time = time.time() - start_time
        slow_response = await slow_task
        total_time = time.time() - start_time

        with capsys.disabled():
            print(f"\nРезультати тесту конкурентності:")
            print(f"✓ Швидкий запит: {fast_time:.2f} сек")
            print(f"✓ Повільний запит: {total_time:.2f} сек")
            print(f"{'✓' if fast_time < 1.0 else '✗'} Статус блокування: {'відсутнє' if fast_time < 1.0 else 'виявлено'}")
        
        assert fast_time < 1.0, f"Виявлено блокування між ендпоінтами: швидкий запит тривав {fast_time:.2f} секунд"
        return fast_time, total_time, fast_response, slow_response

if __name__ == "__main__":
    asyncio.run(test_concurrent_requests())
