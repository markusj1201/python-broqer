import asyncio
import statistics

from broqer import op
from broqer.subject import Subject

adc_raw = Subject()

(adc_raw
 | op.cache(0)
 | op.map(lambda d: d * 5 + 3)
 | op.sample(0.3)
 | op.sliding_window(5)
 | op.map(statistics.mean)
 | op.distinct()
 | op.debounce(0.5)
 | op.sink(print)
 )


async def main():
    await asyncio.sleep(2)
    adc_raw.emit(50)
    await asyncio.sleep(2)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
