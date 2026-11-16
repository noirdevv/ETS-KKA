from datetime import datetime
import os


def save_match_report(filepath, mode, rows, cols, p1_label, p2_label, state, move_logs):
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    winner = state.get_winner()
    winner_txt = {1: f"{p1_label} (P1)", 2: f"{p2_label} (P2)", 0: "Draw"}.get(winner, "None")

    with open(filepath, "a", encoding="utf-8") as f:
        f.write("=" * 68 + "\n")
        f.write(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Mode      : {mode} | Grid: {rows}x{cols}\n")
        f.write(f"Players   : {p1_label} (P1) vs {p2_label} (P2)\n")
        f.write(f"Final     : {state.score[1]} - {state.score[2]} | Winner: {winner_txt}\n")
        f.write("-" * 68 + "\n")

        if not move_logs:
            f.write("No AI moves recorded in this match.\n\n")
            return

        for bot_name in sorted({log["agent"] for log in move_logs}):
            bot_moves = [m for m in move_logs if m["agent"] == bot_name]
            times = [m["time_ms"] for m in bot_moves]
            blunders = sum(1 for m in bot_moves if m["blunder"])
            avg_time = sum(times) / len(times)

            if bot_name == "Minimax":
                avg_nodes = sum(m.get("nodes", 0) for m in bot_moves) / len(bot_moves)
                avg_prunes = sum(m.get("prunes", 0) for m in bot_moves) / len(bot_moves)
                max_depth = max((m.get("depth_reached", 0) for m in bot_moves), default=0)
                detail = (
                    f"Avg Nodes: {avg_nodes:.0f} | Avg Prunes: {avg_prunes:.0f} | "
                    f"Max Depth: {max_depth}"
                )
            else:
                avg_iters = sum(m.get("iterations", 0) for m in bot_moves) / len(bot_moves)
                avg_depth = sum(m.get("max_depth", 0) for m in bot_moves) / len(bot_moves)
                fast_hits = sum(1 for m in bot_moves if m.get("fast_path", False))
                detail = (
                    f"Avg Iters: {avg_iters:.0f} | Avg Tree Depth: {avg_depth:.1f} | "
                    f"Fast Captures: {fast_hits}"
                )

            f.write(
                f"[{bot_name}] Moves: {len(bot_moves)} | "
                f"Avg Time: {avg_time:.2f} ms (Max: {max(times):.2f} ms) | "
                f"Blunders: {blunders} | {detail}\n"
            )
        f.write("\n")