import sys
import json
import os
import re
import random

REPO_OWNER = "quangnhat1504"
REPO_NAME = "quangnhat1504"
STATE_FILE = "data/ttt_state.json"
README_FILE = "README.md"

EMPTY = " "
PLAYER = "X"
AI = "O"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "board": [EMPTY] * 9,
        "last_player": "None",
        "status": "waiting_player",
        "message": "🟢 Đến lượt bạn! Nhấn vào một ô trống để đi nước cờ đầu tiên.",
        "stats": {
            "player_wins": 0,
            "ai_wins": 0,
            "draws": 0,
            "total_games": 0
        }
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def check_winner(board):
    win_patterns = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8), # cols
        (0, 4, 8), (2, 4, 6)             # diags
    ]
    for a, b, c in win_patterns:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    if EMPTY not in board:
        return "DRAW"
    return None

def minimax(board, depth, is_maximizing, alpha=-100, beta=100):
    winner = check_winner(board)
    if winner == AI:
        return 10 - depth
    if winner == PLAYER:
        return depth - 10
    if winner == "DRAW":
        return 0
    if depth >= 6: # limit search depth for subtle mistakes/fun
        return 0

    if is_maximizing:
        max_eval = -1000
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = AI
                eval = minimax(board, depth + 1, False, alpha, beta)
                board[i] = EMPTY
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = 1000
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = PLAYER
                eval = minimax(board, depth + 1, True, alpha, beta)
                board[i] = EMPTY
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def get_best_ai_move(board):
    best_val = -1000
    best_moves = []
    
    # 20% chance of picking a random move on easy turn for fun gameplay
    empty_indices = [i for i in range(9) if board[i] == EMPTY]
    if random.random() < 0.15 and empty_indices:
        return random.choice(empty_indices)

    for i in range(9):
        if board[i] == EMPTY:
            board[i] = AI
            move_val = minimax(board, 0, False)
            board[i] = EMPTY
            if move_val > best_val:
                best_val = move_val
                best_moves = [i]
            elif move_val == best_val:
                best_moves.append(i)
    return random.choice(best_moves) if best_moves else None

def render_board_markdown(state):
    board = state["board"]
    stats = state["stats"]
    msg = state["message"]
    last_player = state.get("last_player", "None")

    issue_base_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/new"
    
    # Render 3x3 table
    table_rows = []
    for r in range(3):
        row_cells = []
        for c in range(3):
            idx = r * 3 + c
            val = board[idx]
            if val == PLAYER:
                cell = "<img src=\"https://img.shields.io/badge/%E2%9D%8C_Bạn-FF1CF7?style=for-the-badge&labelColor=1c1c2e\" alt=\"X\" />"
            elif val == AI:
                cell = "<img src=\"https://img.shields.io/badge/%F0%9F%A4%96_AI-27B2F2?style=for-the-badge&labelColor=1c1c2e\" alt=\"O\" />"
            else:
                if state["status"] in ["player_won", "ai_won", "draw"]:
                    cell = "<img src=\"https://img.shields.io/badge/%E2%9E%95-26263a?style=for-the-badge&labelColor=1c1c2e\" alt=\"Empty\" />"
                else:
                    play_url = f"{issue_base_url}?title=ttt%7Cplay%7C{r}%2C{c}&body=Nh%E1%BA%A5n+%27Submit+new+issue%27+%C4%91%E1%BB%83+ch%E1%BB%8Dn+%C3%B4+n%C3%A0y%21"
                    cell = f"<a href=\"{play_url}\"><img src=\"https://img.shields.io/badge/%E2%9E%95-26263a?style=for-the-badge&labelColor=1c1c2e\" alt=\"Play ({r},{c})\" /></a>"
            row_cells.append(cell)
        table_rows.append(f"| {' | '.join(row_cells)} |")

    table_md = "\n".join([
        "| Cột 1 | Cột 2 | Cột 3 |",
        "| :---: | :---: | :---: |",
        *table_rows
    ])

    new_game_url = f"{issue_base_url}?title=ttt%7Cnew&body=Nh%E1%BA%A5n+%27Submit+new+issue%27+%C4%91%E1%BB%83+b%E1%BA%AFt+%C4%91%E1%BA%A7u+v%C3%A1n+c%E1%BB%9D+m%E1%BB%9Bi%21"

    md_content = f"""<!-- TIC-TAC-TOE:START -->
<div align="center">

### 🕹️ Thách Đấu AI Bot — Tic-Tac-Toe Live Arena ⚔️
*Bấm vào ô `[ ➕ ]` bất kỳ để ra đòn! GitHub Actions Bot sẽ tự động phản hồi nước cờ sau ~10 giây.*

<br/>

{table_md}

<br/>

**Trạng thái trận đấu:** {msg}

<br/>

<a href="{new_game_url}">
  <img src="https://img.shields.io/badge/%F0%9F%94%84_Ch%C6%A1i_V%C3%A1n_M%E1%BB%9Bi_•_Reset_Game-A371F7?style=for-the-badge&labelColor=1c1c2e" alt="Reset Game" />
</a>

<br/><br/>

<sub>🏆 <b>Bảng Thành Tích:</b> Người chơi thắng: <b>{stats['player_wins']}</b> | AI Bot thắng: <b>{stats['ai_wins']}</b> | Hòa: <b>{stats['draws']}</b> • Đấu thủ gần nhất: <b>@{last_player}</b></sub>

</div>
<!-- TIC-TAC-TOE:END -->"""
    return md_content

def update_readme(new_ttt_md):
    if not os.path.exists(README_FILE):
        return
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- TIC-TAC-TOE:START -->.*?<!-- TIC-TAC-TOE:END -->"
    if re.search(pattern, content, flags=re.DOTALL):
        updated = re.sub(pattern, new_ttt_md, content, flags=re.DOTALL)
    else:
        # If not present, replace arcade section
        arcade_pattern = r"<!-- ========================= ARCADE & INTERACTIVE ZONE ========================= -->.*?<img src=\"https://capsule-render\.vercel\.app/api\?type=rect&color=0:FF1CF7,50:A371F7,100:27B2F2&height=3&width=100%&section=header\" width=\"100%\" alt=\"divider\" />"
        replacement = f"""<!-- ========================= ARCADE & INTERACTIVE ZONE ========================= -->
## 🎮 Không Gian Giải Trí & Thách Đấu AI — Arcade Arena

{new_ttt_md}

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:FF1CF7,50:A371F7,100:27B2F2&height=3&width=100%&section=header" width="100%" alt="divider" />"""
        if re.search(arcade_pattern, content, flags=re.DOTALL):
            updated = re.sub(arcade_pattern, replacement, content, flags=re.DOTALL)
        else:
            updated = content + "\n\n" + replacement

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "ttt|init"
    username = sys.argv[2] if len(sys.argv) > 2 else "Visitor"

    state = load_state()
    action = action.strip()

    if action == "ttt|init":
        # Initial render
        md = render_board_markdown(state)
        update_readme(md)
        save_state(state)
        print("Initialized Tic-Tac-Toe.")
        return

    if action.startswith("ttt|new"):
        state["board"] = [EMPTY] * 9
        state["status"] = "in_progress"
        state["last_player"] = username
        state["stats"]["total_games"] += 1
        state["message"] = f"🟢 Ván mới đã bắt đầu bởi @{username}! Bạn đi trước (❌)."
        md = render_board_markdown(state)
        update_readme(md)
        save_state(state)
        print(f"Game reset by @{username}.")
        return

    if action.startswith("ttt|play"):
        parts = action.split("|")
        if len(parts) >= 3:
            coords = parts[2].split(",")
            try:
                r, c = int(coords[0]), int(coords[1])
                idx = r * 3 + c
            except Exception:
                print("Invalid move coordinates.")
                return

            if state["board"][idx] != EMPTY or state["status"] in ["player_won", "ai_won", "draw"]:
                print("Invalid or finished cell.")
                return

            # Player Move
            state["board"][idx] = PLAYER
            state["last_player"] = username
            winner = check_winner(state["board"])

            if winner == PLAYER:
                state["status"] = "player_won"
                state["stats"]["player_wins"] += 1
                state["message"] = f"🎉 Chúc mừng @{username} (❌) đã chiến thắng AI Bot! Nhấn 'Chơi Ván Mới' để bắt đầu trận tiếp theo."
            elif winner == "DRAW":
                state["status"] = "draw"
                state["stats"]["draws"] += 1
                state["message"] = f"🤝 Trận đấu giữa @{username} và AI Bot đã kết thúc với tỷ số HÒA! Nhấn 'Chơi Ván Mới'."
            else:
                # AI Turn
                ai_idx = get_best_ai_move(state["board"])
                if ai_idx is not None:
                    state["board"][ai_idx] = AI
                    ai_winner = check_winner(state["board"])
                    if ai_winner == AI:
                        state["status"] = "ai_won"
                        state["stats"]["ai_wins"] += 1
                        state["message"] = f"🤖 AI Bot (⭕) đã phản công và giành chiến thắng trước @{username}! Đừng nản lòng, hãy nhấn 'Chơi Ván Mới' để phục thù."
                    elif ai_winner == "DRAW":
                        state["status"] = "draw"
                        state["stats"]["draws"] += 1
                        state["message"] = f"🤝 Trận đấu đã kết thúc HÒA sau nước cờ của AI! Nhấn 'Chơi Ván Mới'."
                    else:
                        state["status"] = "in_progress"
                        state["message"] = f"⚔️ @{username} vừa đi ({r+1}, {c+1}). AI Bot đã đáp trả tại ({ai_idx//3+1}, {ai_idx%3+1}). Đến lượt bạn (❌)!"

            md = render_board_markdown(state)
            update_readme(md)
            save_state(state)
            print(f"Move processed for @{username}.")

if __name__ == "__main__":
    main()
