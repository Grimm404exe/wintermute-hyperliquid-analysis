#!/usr/bin/env python3
"""
Generate charts for Wintermute Hyperliquid analysis.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# Style configuration
plt.style.use('dark_background')
COLORS = {
    'blue': '#6B9FFF',
    'green': '#4ADE80',
    'red': '#F87171',
    'orange': '#FB923C',
    'bg': '#1a1b26',
    'text': '#c0caf5',
    'grid': '#3b4261'
}

DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = Path(__file__).parent.parent / "images"


def load_csv(filename):
    """Load CSV file and return list of dicts."""
    with open(DATA_DIR / filename, 'r') as f:
        return list(csv.DictReader(f))


def save_figure(fig, filename):
    """Save figure with consistent styling."""
    fig.patch.set_facecolor(COLORS['bg'])
    fig.savefig(IMAGES_DIR / filename, facecolor=COLORS['bg'], 
                edgecolor='none', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {filename}")


def generate_summary_chart():
    """Generate the main summary metrics chart."""
    orders = load_csv("quoting_strategy_summary.csv")
    
    total_notional = sum(float(r["total_notional_usd"]) for r in orders)
    total_orders = sum(int(r["total_orders"]) for r in orders)
    num_markets = len(orders)
    
    # BTC spread
    btc_row = next((r for r in orders if r["market"] == "BTC"), None)
    btc_spread = float(btc_row["spread_pct"]) if btc_row else 0
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor(COLORS['bg'])
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.92, 'WINTERMUTE', fontsize=32, fontweight='bold', 
            ha='center', va='top', color='white', transform=ax.transAxes)
    ax.text(0.5, 0.82, 'Hyperliquid Market Making Operation', fontsize=16,
            ha='center', va='top', color=COLORS['text'], transform=ax.transAxes,
            family='monospace')
    
    # Divider
    ax.axhline(y=0.75, xmin=0.1, xmax=0.9, color=COLORS['grid'], linewidth=1)
    
    # Metrics - Row 1
    metrics_row1 = [
        (f"${total_notional/1e6:.0f}M", "Total Notional"),
        (f"{total_orders:,}", "Open Orders"),
        (f"{num_markets}", "Markets"),
    ]
    
    for i, (value, label) in enumerate(metrics_row1):
        x = 0.2 + i * 0.3
        ax.text(x, 0.58, value, fontsize=36, fontweight='bold',
                ha='center', va='center', color=COLORS['blue'], transform=ax.transAxes)
        ax.text(x, 0.45, label, fontsize=14, ha='center', va='center',
                color=COLORS['text'], transform=ax.transAxes, family='monospace')
    
    # Metrics - Row 2
    metrics_row2 = [
        (f"{btc_spread:.2f}%", "BTC Spread"),
        ("11", "Size Tiers"),
        ("2.6x", "Tier Multiplier"),
    ]
    
    for i, (value, label) in enumerate(metrics_row2):
        x = 0.2 + i * 0.3
        ax.text(x, 0.28, value, fontsize=36, fontweight='bold',
                ha='center', va='center', color=COLORS['blue'], transform=ax.transAxes)
        ax.text(x, 0.15, label, fontsize=14, ha='center', va='center',
                color=COLORS['text'], transform=ax.transAxes, family='monospace')
    
    # Footer
    ax.text(0.5, 0.05, 'Wallet: 0xecb63caa47c7c4e77f60f1ce858cf28dc2b82b00',
            fontsize=10, ha='center', color=COLORS['grid'], transform=ax.transAxes,
            family='monospace')
    ax.text(0.5, 0.01, 'Data: January 2026', fontsize=10, ha='center',
            color=COLORS['grid'], transform=ax.transAxes, family='monospace')
    
    save_figure(fig, "chart_summary.png")


def generate_account_summary_chart():
    """Generate account summary with total value including spot."""
    positions = load_csv("positions.csv")
    balances = load_csv("balances.csv")
    orders = load_csv("quoting_strategy_summary.csv")
    
    # Calculate spot value
    spot_value = sum(float(r["entry_notional"]) for r in balances)
    # Add USDC at face value (entry_notional is 0 for USDC)
    usdc_row = next((r for r in balances if r["coin"] == "USDC"), None)
    if usdc_row:
        spot_value += float(usdc_row["total"])
    
    # Perp account value (margin + unrealized PnL)
    # Using position data to estimate
    total_margin = sum(float(r["margin_used"]) for r in positions)
    total_pnl = sum(float(r["unrealized_pnl"]) for r in positions)
    
    # Perp account value from original data
    perp_account = 57.8e6  # From original analysis
    
    # Total account value
    total_account = perp_account + spot_value
    
    # Position stats
    position_notional = sum(abs(float(r["position_value"])) for r in positions)
    long_notional = sum(float(r["position_value"]) for r in positions if r["side"] == "LONG")
    short_notional = sum(abs(float(r["position_value"])) for r in positions if r["side"] == "SHORT")
    net_exposure = long_notional - short_notional
    
    total_orders = sum(int(r["total_orders"]) for r in orders)
    num_positions = len(positions)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor(COLORS['bg'])
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.92, 'WINTERMUTE', fontsize=32, fontweight='bold',
            ha='center', va='top', color='white', transform=ax.transAxes)
    ax.text(0.5, 0.82, 'Hyperliquid Account Summary', fontsize=16,
            ha='center', va='top', color=COLORS['text'], transform=ax.transAxes,
            family='monospace')
    
    ax.axhline(y=0.75, xmin=0.1, xmax=0.9, color=COLORS['grid'], linewidth=1)
    
    # Row 1 - Account values
    metrics_row1 = [
        (f"${total_account/1e6:.0f}M", "Total Account"),
        (f"${position_notional/1e6:.0f}M", "Position Notional"),
        (f"${abs(net_exposure)/1e6:.0f}M", "Net SHORT" if net_exposure < 0 else "Net LONG"),
    ]
    
    for i, (value, label) in enumerate(metrics_row1):
        x = 0.2 + i * 0.3
        color = COLORS['red'] if 'SHORT' in label else COLORS['blue']
        ax.text(x, 0.58, value, fontsize=36, fontweight='bold',
                ha='center', va='center', color=color, transform=ax.transAxes)
        ax.text(x, 0.45, label, fontsize=14, ha='center', va='center',
                color=COLORS['text'], transform=ax.transAxes, family='monospace')
    
    # Row 2
    metrics_row2 = [
        (f"${total_pnl/1e6:.1f}M", "Unrealized PnL"),
        (f"{num_positions}", "Positions"),
        (f"{total_orders:,}", "Open Orders"),
    ]
    
    for i, (value, label) in enumerate(metrics_row2):
        x = 0.2 + i * 0.3
        color = COLORS['red'] if total_pnl < 0 else COLORS['green']
        if i > 0:
            color = COLORS['blue']
        ax.text(x, 0.28, value, fontsize=36, fontweight='bold',
                ha='center', va='center', color=color, transform=ax.transAxes)
        ax.text(x, 0.15, label, fontsize=14, ha='center', va='center',
                color=COLORS['text'], transform=ax.transAxes, family='monospace')
    
    ax.text(0.5, 0.05, 'Wallet: 0xecb63caa47c7c4e77f60f1ce858cf28dc2b82b00',
            fontsize=10, ha='center', color=COLORS['grid'], transform=ax.transAxes,
            family='monospace')
    ax.text(0.5, 0.01, 'Data: January 2026', fontsize=10, ha='center',
            color=COLORS['grid'], transform=ax.transAxes, family='monospace')
    
    save_figure(fig, "chart_account_summary.png")


def generate_market_notional_chart():
    """Generate top markets by notional bar chart."""
    orders = load_csv("quoting_strategy_summary.csv")
    
    # Sort by notional and take top 15
    orders_sorted = sorted(orders, key=lambda x: float(x["total_notional_usd"]), reverse=True)[:15]
    
    markets = [r["market"] for r in orders_sorted]
    notionals = [float(r["total_notional_usd"]) / 1e6 for r in orders_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor(COLORS['bg'])
    
    # Color based on whether it's a standard perp or spot market
    colors = [COLORS['blue'] if not r["market"].startswith('@') else COLORS['orange'] 
              for r in orders_sorted]
    
    bars = ax.barh(range(len(markets)), notionals, color=colors, edgecolor='none')
    
    ax.set_yticks(range(len(markets)))
    ax.set_yticklabels(markets, fontsize=12, color=COLORS['text'])
    ax.invert_yaxis()
    
    ax.set_xlabel('Notional Value ($ Millions)', fontsize=12, color=COLORS['text'], 
                  family='monospace')
    ax.tick_params(axis='x', colors=COLORS['text'])
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, notionals)):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'${val:.1f}M', va='center', fontsize=10, color=COLORS['text'])
    
    ax.set_title('WINTERMUTE ON HYPERLIQUID\nTop 15 Markets by Notional Value',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.spines['left'].set_color(COLORS['grid'])
    ax.grid(axis='x', color=COLORS['grid'], alpha=0.3)
    
    save_figure(fig, "chart_market_notional.png")


def generate_bid_ask_balance_chart():
    """Generate bid/ask balance comparison chart."""
    orders = load_csv("quoting_strategy_summary.csv")
    
    # Sort and take top 10
    orders_sorted = sorted(orders, key=lambda x: float(x["total_notional_usd"]), reverse=True)[:10]
    
    markets = [r["market"] for r in orders_sorted]
    bids = [float(r["bid_notional_usd"]) / 1e6 for r in orders_sorted]
    asks = [float(r["ask_notional_usd"]) / 1e6 for r in orders_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor(COLORS['bg'])
    
    x = np.arange(len(markets))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, bids, width, label='Bid Notional', color=COLORS['green'])
    bars2 = ax.bar(x + width/2, asks, width, label='Ask Notional', color=COLORS['red'])
    
    ax.set_ylabel('Notional Value ($ Millions)', fontsize=12, color=COLORS['text'],
                  family='monospace')
    ax.set_xlabel('Market', fontsize=12, color=COLORS['text'], family='monospace')
    ax.set_xticks(x)
    ax.set_xticklabels(markets, fontsize=11, color=COLORS['text'])
    ax.tick_params(axis='y', colors=COLORS['text'])
    
    ax.legend(loc='upper right', facecolor=COLORS['bg'], edgecolor=COLORS['grid'],
              labelcolor=COLORS['text'])
    
    ax.set_title('WINTERMUTE BID/ASK SYMMETRY\nNearly Balanced Exposure Across Markets',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.spines['left'].set_color(COLORS['grid'])
    ax.grid(axis='y', color=COLORS['grid'], alpha=0.3)
    
    save_figure(fig, "chart_bid_ask_balance.png")


def generate_btc_depth_chart():
    """Generate BTC order book depth chart."""
    detailed = load_csv("quoting_strategy_detailed.csv")
    
    # Filter BTC orders
    btc_orders = [r for r in detailed if r["market"] == "BTC"]
    if not btc_orders:
        print("No BTC orders found")
        return
    
    bids = [(float(r["price"]), float(r["size"])) for r in btc_orders if r["side"] == "BID"]
    asks = [(float(r["price"]), float(r["size"])) for r in btc_orders if r["side"] == "ASK"]
    
    bids.sort(key=lambda x: x[0], reverse=True)
    asks.sort(key=lambda x: x[0])
    
    # Calculate cumulative sizes
    bid_prices = [b[0] for b in bids]
    bid_cum = np.cumsum([b[1] for b in bids])
    
    ask_prices = [a[0] for a in asks]
    ask_cum = np.cumsum([a[1] for a in asks])
    
    mid_price = (bids[0][0] + asks[0][0]) / 2 if bids and asks else 0
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor(COLORS['bg'])
    
    # Plot as step functions
    ax.fill_between(bid_prices, bid_cum, step='post', alpha=0.7, color=COLORS['green'], label='Bid Depth')
    ax.fill_between(ask_prices, ask_cum, step='post', alpha=0.7, color=COLORS['red'], label='Ask Depth')
    
    ax.axvline(x=mid_price, color=COLORS['orange'], linestyle='--', linewidth=2, 
               label=f'Mid: ${mid_price:,.0f}')
    
    ax.set_xlabel('Price (USD)', fontsize=12, color=COLORS['text'], family='monospace')
    ax.set_ylabel('Cumulative Size (BTC)', fontsize=12, color=COLORS['text'], family='monospace')
    ax.tick_params(colors=COLORS['text'])
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x/1000:.1f}k'))
    
    ax.legend(loc='upper right', facecolor=COLORS['bg'], edgecolor=COLORS['grid'],
              labelcolor=COLORS['text'])
    
    ax.set_title('WINTERMUTE BTC ORDER BOOK DEPTH\nCumulative Size at Each Price Level',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.spines['left'].set_color(COLORS['grid'])
    
    save_figure(fig, "chart_btc_depth.png")


def generate_size_tiers_chart():
    """Generate BTC size tiers scatter plot."""
    detailed = load_csv("quoting_strategy_detailed.csv")
    
    btc_orders = [r for r in detailed if r["market"] == "BTC"]
    if not btc_orders:
        print("No BTC orders found")
        return
    
    # Group by size to find tiers
    sizes = {}
    for order in btc_orders:
        size = round(float(order["size"]), 2)
        dist = float(order.get("distance_from_mid_bps", 0)) / 100  # Convert to %
        if size not in sizes:
            sizes[size] = {"count": 0, "avg_dist": 0, "dists": []}
        sizes[size]["count"] += 1
        sizes[size]["dists"].append(dist)
    
    for size in sizes:
        sizes[size]["avg_dist"] = np.mean(sizes[size]["dists"])
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor(COLORS['bg'])
    
    for size, data in sizes.items():
        ax.scatter(data["avg_dist"], size, s=data["count"] * 100, 
                   alpha=0.7, color=COLORS['blue'], edgecolors='white', linewidth=1)
        ax.annotate(f'{data["count"]} orders', (data["avg_dist"], size),
                    xytext=(10, 0), textcoords='offset points',
                    fontsize=9, color=COLORS['text'])
    
    ax.set_xlabel('Distance from Mid Price (%)', fontsize=12, color=COLORS['text'],
                  family='monospace')
    ax.set_ylabel('Order Size (BTC)', fontsize=12, color=COLORS['text'], family='monospace')
    ax.set_yscale('log')
    ax.tick_params(colors=COLORS['text'])
    
    ax.set_title('WINTERMUTE BTC SIZE TIERS\nLarger Sizes Deployed Further from Mid',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.spines['left'].set_color(COLORS['grid'])
    ax.grid(True, color=COLORS['grid'], alpha=0.3)
    
    save_figure(fig, "chart_size_tiers.png")


def generate_spot_balances_chart():
    """Generate spot balances bar chart."""
    balances = load_csv("balances.csv")
    
    # Filter and sort by entry notional
    balances_sorted = sorted(balances, key=lambda x: float(x["entry_notional"]), reverse=True)
    
    # Take top holdings (filter out tiny amounts)
    top_balances = [b for b in balances_sorted if float(b["entry_notional"]) > 100000][:10]
    
    # Add USDC separately
    usdc = next((b for b in balances if b["coin"] == "USDC"), None)
    if usdc and usdc not in top_balances:
        top_balances.append(usdc)
    
    coins = [b["coin"] for b in top_balances]
    values = [max(float(b["entry_notional"]), float(b["total"]) if b["coin"] == "USDC" else 0) / 1e6 
              for b in top_balances]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor(COLORS['bg'])
    
    colors = [COLORS['green'] if c in ['USDC', 'USDT0', 'USDH'] else COLORS['blue'] 
              for c in coins]
    
    bars = ax.barh(range(len(coins)), values, color=colors, edgecolor='none')
    
    ax.set_yticks(range(len(coins)))
    ax.set_yticklabels(coins, fontsize=12, color=COLORS['text'])
    ax.invert_yaxis()
    
    ax.set_xlabel('Value ($ Millions)', fontsize=12, color=COLORS['text'], family='monospace')
    ax.tick_params(axis='x', colors=COLORS['text'])
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'${val:.1f}M', va='center', fontsize=10, color=COLORS['text'])
    
    ax.set_title('WINTERMUTE SPOT HOLDINGS\nTop Token Balances by Value',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.spines['left'].set_color(COLORS['grid'])
    ax.grid(axis='x', color=COLORS['grid'], alpha=0.3)
    
    save_figure(fig, "chart_spot_balances.png")


def generate_positions_chart():
    """Generate top positions bar chart."""
    positions = load_csv("positions.csv")
    
    # Sort by absolute position value
    positions_sorted = sorted(positions, key=lambda x: abs(float(x["position_value"])), reverse=True)[:15]
    
    coins = [p["coin"] for p in positions_sorted]
    values = [float(p["position_value"]) / 1e6 for p in positions_sorted]
    sides = [p["side"] for p in positions_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor(COLORS['bg'])
    
    colors = [COLORS['green'] if s == 'LONG' else COLORS['red'] for s in sides]
    
    bars = ax.barh(range(len(coins)), [abs(v) for v in values], color=colors, edgecolor='none')
    
    ax.set_yticks(range(len(coins)))
    ax.set_yticklabels([f"{c} ({s})" for c, s in zip(coins, sides)], fontsize=11, color=COLORS['text'])
    ax.invert_yaxis()
    
    ax.set_xlabel('Position Value ($ Millions)', fontsize=12, color=COLORS['text'], family='monospace')
    ax.tick_params(axis='x', colors=COLORS['text'])
    
    for bar, val, side in zip(bars, values, sides):
        label = f'${abs(val):.1f}M'
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                label, va='center', fontsize=10, color=COLORS['text'])
    
    ax.set_title('WINTERMUTE PERP POSITIONS\nTop 15 by Notional Value',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.spines['left'].set_color(COLORS['grid'])
    ax.grid(axis='x', color=COLORS['grid'], alpha=0.3)
    
    save_figure(fig, "chart_positions.png")


def generate_long_short_chart():
    """Generate long/short exposure pie chart."""
    positions = load_csv("positions.csv")
    
    long_val = sum(float(p["position_value"]) for p in positions if p["side"] == "LONG")
    short_val = sum(abs(float(p["position_value"])) for p in positions if p["side"] == "SHORT")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor(COLORS['bg'])
    
    sizes = [long_val, short_val]
    labels = [f'LONG\n${long_val/1e6:.1f}M', f'SHORT\n${short_val/1e6:.1f}M']
    colors_pie = [COLORS['green'], COLORS['red']]
    
    wedges, texts = ax.pie(sizes, labels=labels, colors=colors_pie,
                           startangle=90, labeldistance=1.15,
                           wedgeprops={'edgecolor': COLORS['bg'], 'linewidth': 2})
    
    for text in texts:
        text.set_color(COLORS['text'])
        text.set_fontsize(14)
        text.set_fontweight('bold')
    
    ax.set_title('WINTERMUTE EXPOSURE\nLong vs Short Position Value',
                 fontsize=16, fontweight='bold', color='white', family='monospace', pad=20)
    
    save_figure(fig, "chart_long_short.png")


def main():
    print("Generating Wintermute analysis charts...")
    print("=" * 50)
    
    IMAGES_DIR.mkdir(exist_ok=True)
    
    generate_summary_chart()
    generate_account_summary_chart()
    generate_market_notional_chart()
    generate_bid_ask_balance_chart()
    generate_btc_depth_chart()
    generate_size_tiers_chart()
    generate_spot_balances_chart()
    generate_positions_chart()
    generate_long_short_chart()
    
    print("=" * 50)
    print("Done! Charts saved to images/ directory.")


if __name__ == "__main__":
    main()
