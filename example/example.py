import time
import uuid

import slate

if __name__ == "__main__":
    slate = slate.Slate()

    # Tell the platform that the model is running
    slate.model.model_livecycle(message='Running', start_at=slate.now, running=True)

    # Tell the platform we're running live on alpaca & AAPL
    slate.model.used_exchange('alpaca')
    slate.model.used_symbol('AAPL')

    while True:
        # Simulate market order to the platform & report a trade on each loop
        print(slate.live.spot_market('AAPL', 'alpaca', uuid.uuid4(), 'buy', 1, annotation='RSI Low'))

        # Loop the model
        time.sleep(100)
