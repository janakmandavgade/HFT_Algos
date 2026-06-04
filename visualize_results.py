import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import os


def plot_saved_avellaneda_results(
    curve_file,
    run_name=None,
    max_inventory=5,
    zoom=500_000,
    save_path=None
):
    df = pd.read_csv(curve_file)

    if run_name is None:
        run_name = os.path.basename(curve_file).replace("_curves.csv", "")

    zoom = min(zoom, len(df))

    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(12, 10),
        sharex=False
    )

    ax1.plot(
        df["equity"],
        color="green",
        linewidth=1.5,
        label="Total Account Value"
    )
    ax1.set_title(
        f"Avellaneda-Stoikov HFT Simulation Results - {run_name}",
        fontsize=14,
        fontweight="bold"
    )
    ax1.set_ylabel("Portfolio Value ($)", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left")

    ax2.plot(
        df["inventory"],
        color="purple",
        linewidth=1.2,
        label="Inventory (q)"
    )
    ax2.axhline(0, color="black", linestyle="-", alpha=0.4)
    ax2.axhline(
        max_inventory,
        color="red",
        linestyle=":",
        alpha=0.6,
        label="Max Long"
    )
    ax2.axhline(
        -max_inventory,
        color="red",
        linestyle=":",
        alpha=0.6,
        label="Max Short"
    )
    ax2.set_ylabel("Position Size (Tokens)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper left")

    ax3.plot(
        df["spot_price"].iloc[:zoom],
        color="black",
        label="Market Mid-Price",
        linewidth=1.5
    )
    ax3.plot(
        df["ask_quote"].iloc[:zoom],
        color="red",
        label="Our Ask Order",
        linestyle="--",
        alpha=0.8
    )
    ax3.plot(
        df["bid_quote"].iloc[:zoom],
        color="blue",
        label="Our Bid Order",
        linestyle="--",
        alpha=0.8
    )
    ax3.set_title(
        f"Quote Behavior - First {zoom:,} Simulation Ticks",
        fontsize=12
    )
    ax3.set_ylabel("Asset Price ($)", fontsize=11)
    ax3.set_xlabel("Simulation Ticks", fontsize=11)
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.legend(loc="upper left")

    plt.tight_layout()

    if save_path is None:
        os.makedirs("plots", exist_ok=True)
        save_path = f"plots/{run_name}_dashboard.png"

    save_dir = os.path.dirname(save_path)

    if save_dir != "":
        os.makedirs(save_dir, exist_ok=True)

    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Saved plot to: {save_path}")

    plt.close(fig)

    
plot_saved_avellaneda_results(
    curve_file="outputs/rf_010_k_150_inv_5_26_curves.csv",
    run_name="rf_010_k_150_inv_5_26",
    max_inventory=5,
    zoom=500_000,
    save_path="plots/rf_010_k_150_inv_5_26_dashboard.png"
)
plot_saved_avellaneda_results(
    curve_file="outputs/rf_010_k_150_inv_5_27_curves.csv",
    run_name="rf_010_k_150_inv_5_27",
    max_inventory=5,
    zoom=500_000,
    save_path="plots/rf_010_k_150_inv_5_27_dashboard.png"
)

plot_saved_avellaneda_results(
    curve_file="outputs/rf_010_k_150_inv_5_28_curves.csv",
    run_name="rf_010_k_150_inv_5_28",
    max_inventory=5,
    zoom=500_000,
    save_path="plots/rf_010_k_150_inv_5_28_dashboard.png"
)

plot_saved_avellaneda_results(
    curve_file="outputs/rf_010_k_150_inv_5_29_curves.csv",
    run_name="rf_010_k_150_inv_5_29",
    max_inventory=5,
    zoom=500_000,
    save_path="plots/rf_010_k_150_inv_5_29_dashboard.png"
)

plot_saved_avellaneda_results(
    curve_file="outputs/rf_010_k_150_inv_5_30_curves.csv",
    run_name="rf_010_k_150_inv_5_30",
    max_inventory=5,
    zoom=500_000,
    save_path="plots/rf_010_k_150_inv_5_30_dashboard.png"
)