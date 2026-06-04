import os
import traceback
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed


def run_avellaneda_simulation(
    csv_file,
    risk_factor=0.1,
    kappa=150.0,
    max_inventory=5,
    start_loop=1001,
    max_ticks=5_000_000,
    run_name="default",
    output_dir="outputs"
):
    try:
        os.makedirs(output_dir, exist_ok=True)

        # Read only needed columns to reduce RAM
        df = pd.read_csv(
            csv_file,
            usecols=["best_ask_price", "best_bid_price", "event_time"]
        )

        df["spot_price"] = (
            df["best_ask_price"] + df["best_bid_price"]
        ) / 2

        inventory_q = 0
        cash = 100000.0

        equity_curve = []
        inventory_history = []
        price_ask_list = []
        price_bid_list = []
        spot_price_history = []

        spot_prices = df["spot_price"].to_numpy()
        best_bids = df["best_bid_price"].to_numpy()
        best_asks = df["best_ask_price"].to_numpy()
        event_times = df["event_time"].to_numpy()

        if len(spot_prices) <= start_loop:
            raise ValueError(
                f"{run_name}: Not enough rows. "
                f"Rows={len(spot_prices)}, start_loop={start_loop}"
            )

        end_time = event_times[-1]
        start_time = event_times[0]
        total_time = end_time - start_time

        if total_time == 0:
            raise ValueError(f"{run_name}: total_time is zero.")

        active_bid = None
        active_ask = None

        end_loop = min(max_ticks, len(spot_prices) - 1)

        for i in range(start_loop, end_loop):
            current_spot_price = spot_prices[i]
            current_market_bid = best_bids[i]
            current_market_ask = best_asks[i]

            # Simulate fills
            if active_bid is not None:
                if current_market_bid <= active_bid and inventory_q < max_inventory:
                    inventory_q += 1
                    cash -= active_bid

            if active_ask is not None:
                if current_market_ask >= active_ask and inventory_q > -max_inventory:
                    inventory_q -= 1
                    cash += active_ask

            current_equity = cash + inventory_q * current_spot_price

            equity_curve.append(current_equity)
            inventory_history.append(inventory_q)
            spot_price_history.append(current_spot_price)

            historical_values = spot_prices[i - 1000:i]
            variance = np.var((historical_values / current_spot_price) * 100)

            time_left = end_time - event_times[i]
            t_remaining = time_left / total_time

            reservation_price = 100.0 - (
                inventory_q * risk_factor * variance * t_remaining
            )

            delta = (
                0.5 * risk_factor * variance * t_remaining
                + (1 / risk_factor) * np.log(1 + risk_factor / kappa)
            )

            price_ask_norm = reservation_price + delta
            price_bid_norm = reservation_price - delta

            active_ask = (price_ask_norm / 100.0) * current_spot_price
            active_bid = (price_bid_norm / 100.0) * current_spot_price

            price_ask_list.append(active_ask)
            price_bid_list.append(active_bid)

        if len(equity_curve) == 0:
            raise ValueError(f"{run_name}: No simulation ticks were processed.")

        final_equity = equity_curve[-1]
        pnl = final_equity - 100000.0

        # Save full curves inside the worker process
        curve_df = pd.DataFrame({
            "spot_price": spot_price_history,
            "equity": equity_curve,
            "inventory": inventory_history,
            "ask_quote": price_ask_list,
            "bid_quote": price_bid_list,
        })

        curve_file = os.path.join(output_dir, f"{run_name}_curves.csv")
        curve_df.to_csv(curve_file, index=False)

        # Return only small summary, not millions of data points
        return {
            "status": "success",
            "run_name": run_name,
            "csv_file": csv_file,
            "risk_factor": risk_factor,
            "kappa": kappa,
            "max_inventory": max_inventory,
            "final_equity": final_equity,
            "pnl": pnl,
            "final_inventory": inventory_q,
            "num_ticks": len(equity_curve),
            "curve_file": curve_file,
        }

    except Exception as e:
        return {
            "status": "failed",
            "run_name": run_name,
            "csv_file": csv_file,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


if __name__ == "__main__":

    configs = [
        {
            "csv_file": "./BTCUSDT-bookTicker-2024-03-26/BTCUSDT-bookTicker-2024-03-26.csv",
            "risk_factor": 0.10,
            "kappa": 150.0,
            "max_inventory": 5,
            "run_name": "rf_010_k_150_inv_5_26"
        },
        {
            "csv_file": "./BTCUSDT-bookTicker-2024-03-27/BTCUSDT-bookTicker-2024-03-27.csv",
            "risk_factor": 0.10,
            "kappa": 150.0,
            "max_inventory": 5,
            "run_name": "rf_010_k_150_inv_5_27"
        },
        {
            "csv_file": "./BTCUSDT-bookTicker-2024-03-28/BTCUSDT-bookTicker-2024-03-28.csv",
            "risk_factor": 0.10,
            "kappa": 150.0,
            "max_inventory": 5,
            "run_name": "rf_010_k_150_inv_5_28"
        },
        {
            "csv_file": "./BTCUSDT-bookTicker-2024-03-29/BTCUSDT-bookTicker-2024-03-29.csv",
            "risk_factor": 0.10,
            "kappa": 150.0,
            "max_inventory": 5,
            "run_name": "rf_010_k_150_inv_5_29"
        },
        {
            "csv_file": "./BTCUSDT-bookTicker-2024-03-30/BTCUSDT-bookTicker-2024-03-30.csv",
            "risk_factor": 0.10,
            "kappa": 150.0,
            "max_inventory": 5,
            "run_name": "rf_010_k_150_inv_5_30"
        }
    ]

    max_workers = 1
    results = []
    failures = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(run_avellaneda_simulation, **config)
            for config in configs
        ]

        for future in as_completed(futures):
            result = future.result()

            if result["status"] == "success":
                results.append(result)

                print(
                    f"Finished {result['run_name']} | "
                    f"PnL: {result['pnl']:.2f} | "
                    f"Final equity: {result['final_equity']:.2f} | "
                    f"Ticks: {result['num_ticks']}"
                )

            else:
                failures.append(result)

                print(f"FAILED: {result['run_name']}")
                print(result["error"])
                print(result["traceback"])

    summary_df = pd.DataFrame(results)
    summary_df.to_csv("simulation_summary.csv", index=False)

    if failures:
        failure_df = pd.DataFrame(failures)
        failure_df.to_csv("simulation_failures.csv", index=False)

    print("\nSummary:")
    print(summary_df)