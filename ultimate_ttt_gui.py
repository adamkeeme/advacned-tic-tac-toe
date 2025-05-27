from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from functools import partial
from typing import List, Optional, Tuple

import tic_tac_toe as core
import ai_bots
from constants import PLAYER_X, PLAYER_O

# START SCREEN
class StartScreen(tk.Frame):
    def __init__(self, master: tk.Tk, launch_game_callback):
        super().__init__(master, padx=20, pady=20)
        self.master = master
        self.pack(expand=True)
        self.launch_game_callback = launch_game_callback

        tk.Label(self, text="Tic-Tac-Toe", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        game_type_frame = tk.Frame(self); game_type_frame.pack(pady=5)
        tk.Label(game_type_frame, text="Game Type:").pack(side=tk.LEFT)
        self.game_type_var = tk.StringVar(value="ultimate")
        for type_val, type_text in [("classic", "Classic"), ("ultimate", "Ultimate")]:
            tk.Radiobutton(game_type_frame, text=type_text, variable=self.game_type_var, value=type_val).pack(side=tk.LEFT)

        difficulty_frame = tk.Frame(self); difficulty_frame.pack(pady=5)
        tk.Label(difficulty_frame, text="AI Difficulty:").pack(side=tk.LEFT)
        self.difficulty_var = tk.StringVar(value="medium")
        for diff_val, diff_text in [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]:
            tk.Radiobutton(difficulty_frame, text=diff_text, variable=self.difficulty_var, value=diff_val).pack(side=tk.LEFT)

        start_button = tk.Button(self, text="Start Game", command=self.start_game_action, font=("Arial", 12))
        start_button.pack(pady=15)

    def start_game_action(self):
        self.launch_game_callback(self.game_type_var.get(), self.difficulty_var.get())
        self.pack_forget(); self.destroy()

# CLASSIC TICTACTOE GUI
class ClassicGameGUI(tk.Frame):
    def __init__(self, master: tk.Tk, difficulty: str):
        super().__init__(master, padx=10, pady=10)
        self.master = master; self.difficulty = difficulty
        self.player_char, self.ai_char = PLAYER_X, PLAYER_O
        self.current_player_is_human, self.game_over = True, False
        self.pack(expand=True, fill=tk.BOTH)

        self.status_var = tk.StringVar(value=f"Your turn ({self.player_char}) - Diff: {difficulty.title()}")
        tk.Label(self, textvariable=self.status_var, font=("Arial", 12)).pack(pady=(0,10))

        self.board_logic = core.SmallBoard() # Uses 'core' alias for tic_tac_toe.py
        self.buttons: List[tk.Button] = []
        self.create_board_widgets()

    def create_board_widgets(self):
        board_frame = tk.Frame(self); board_frame.pack(pady=10)
        for i in range(9):
            r, c = divmod(i, 3)
            btn = tk.Button(board_frame, text=str(i+1), font=("Arial",14,"bold"), width=4, height=2, command=partial(self.handle_player_click,i))
            btn.grid(row=r, column=c, padx=2, pady=2); self.buttons.append(btn)

    def update_status(self, msg:str): self.status_var.set(msg)

    def handle_player_click(self, index: int):
        if self.game_over or not self.current_player_is_human or not self.board_logic.is_empty(index): return # Uses .is_empty
        self.apply_move(index, self.player_char)
        if not self.game_over:
            self.current_player_is_human = False
            self.update_status(f"Computer ({self.ai_char}) thinking...")
            self.master.update_idletasks()
            self.after(100, self.ai_move)

    def ai_move(self):
        if self.game_over: return
        move = ai_bots.choose_move_small(self.board_logic, self.difficulty) # Uses ai_bots
        self.apply_move(move, self.ai_char)
        if not self.game_over:
            self.current_player_is_human = True
            self.update_status(f"Your turn ({self.player_char})")

    def apply_move(self, index: int, player_char: str):
        self.board_logic.mark_square(index, player_char) # Uses .mark_square
        btn = self.buttons[index]
        btn.config(text=player_char, state=tk.DISABLED, disabledforeground="blue" if player_char == PLAYER_X else "red")
        if self.board_logic.winner: # Uses .winner
            self.game_over = True
            msg = "Draw!" if self.board_logic.winner=="D" else f"{self.board_logic.winner} wins!"
            self.update_status(msg); messagebox.showinfo("Game Over", msg, parent=self)
            for b in self.buttons: b.config(state=tk.DISABLED)

# ULTIMATE TICTACTOE GUI
class UltimateGameGUI(tk.Frame):
    def __init__(self, master: tk.Tk, difficulty: str):
        super().__init__(master, padx=10, pady=10)
        self.master = master; self.difficulty = difficulty
        self.player_char, self.ai_char = PLAYER_X, PLAYER_O
        self.current_player_is_human, self.game_over = True, False
        self.pack(expand=True, fill=tk.BOTH)

        self.status_var = tk.StringVar(value=f"Your turn ({self.player_char}) - Diff: {difficulty.title()}")
        tk.Label(self, textvariable=self.status_var, font=("Arial", 12)).pack(pady=(0,10))

        self.board_logic = core.UltimateBoard() # Uses 'core' alias
        self.small_board_buttons: List[List[tk.Button]] = [[] for _ in range(9)]
        self.small_board_frames: List[tk.Frame] = []
        self.current_forced_board_idx: Optional[int] = None
        self.create_board_widgets(); self.update_board_highlights()

    def create_board_widgets(self):
        ultimate_frame = tk.Frame(self); ultimate_frame.pack(pady=5,padx=5)
        for i in range(9):
            br, bc = divmod(i,3)
            sb_frame = tk.Frame(ultimate_frame, relief=tk.SOLID, borderwidth=1)
            sb_frame.grid(row=br, column=bc, padx=3, pady=3); self.small_board_frames.append(sb_frame)
            for j in range(9):
                sr, sc = divmod(j,3)
                btn = tk.Button(sb_frame, text=str(j+1), font=("Arial",10,"bold"), width=3,height=1, command=partial(self.handle_player_click,i,j))
                btn.grid(row=sr,column=sc,padx=1,pady=1); self.small_board_buttons[i].append(btn)

    def update_status(self, msg:str): self.status_var.set(msg)

    def handle_player_click(self, sb_idx: int, sq_idx: int):
        if self.game_over or not self.current_player_is_human: return
        target_sb = self.board_logic.small_boards[sb_idx] 
        available_b = self.board_logic.get_available_small_board_indices(self.current_forced_board_idx)
        if sb_idx not in available_b: self.update_status("Invalid: Play in highlighted board."); return
        if not target_sb.is_empty(sq_idx): self.update_status("Invalid: Square taken."); return
        
        self.apply_move(sb_idx, sq_idx, self.player_char)
        if not self.game_over:
            self.current_player_is_human = False
            self.update_status(f"Computer ({self.ai_char}) thinking...")
            self.master.update_idletasks(); self.after(100, self.ai_move)

    def ai_move(self):
        if self.game_over: return
        b_idx,s_idx = ai_bots.choose_move(self.board_logic,self.current_forced_board_idx,self.difficulty)
        self.apply_move(b_idx,s_idx,self.ai_char)
        if not self.game_over:
            self.current_player_is_human=True
            self. update_status(f"Your turn ({self.player_char})")

    def apply_move(self, sb_idx: int, sq_idx: int, player_char: str):
        self.current_forced_board_idx = self.board_logic.make_move(sb_idx, sq_idx, player_char)
        btn = self.small_board_buttons[sb_idx][sq_idx]
        btn.config(text=player_char, state=tk.DISABLED, disabledforeground="blue" if player_char==PLAYER_X else "red")
        
        sb_played = self.board_logic.small_boards[sb_idx] 
        if sb_played.winner: 
            frame_bg = "light gray" if sb_played.winner=="D" else ("lightblue" if sb_played.winner==PLAYER_X else "lightcoral")
            self.small_board_frames[sb_idx].config(bg=frame_bg)
            for b in self.small_board_buttons[sb_idx]: b.config(state=tk.DISABLED)
        
        if self.board_logic.overall_winner: 
            self.game_over=True
            winner=self.board_logic.overall_winner
            msg = "Draw!" if winner=="D" else f"Player {winner} wins!"
            self.update_status(msg); messagebox.showinfo("Game Over",msg,parent=self)
            
            for i in range(9): # disable all buttons and reset highlights
                for b_in_sb in self.small_board_buttons[i]: b_in_sb.config(state=tk.DISABLED)
                self.small_board_frames[i].config(relief=tk.SOLID, borderwidth=1, bg=self.master.cget('bg') if not self.board_logic.small_boards[i].winner else self.small_board_frames[i].cget('bg')) # Reset non-won boards
        else:
            self.update_board_highlights()
            if self.current_player_is_human:
                next_active = self.board_logic.get_available_small_board_indices(self.current_forced_board_idx)
                if len(next_active)==1 and self.board_logic.small_boards[next_active[0]].winner is None:
                    self.update_status(f"Your turn ({self.player_char}). Play in board {next_active[0]+1}.")
                else: self.update_status(f"Your turn ({self.player_char}). Free move.")


    def update_board_highlights(self):
        if self.game_over: return
        available_next = self.board_logic.get_available_small_board_indices(self.current_forced_board_idx)
        for i, frame in enumerate(self.small_board_frames):
            is_active = (self.board_logic.small_boards[i].winner is None and i in available_next)
            frame.config(relief=tk.RIDGE if is_active else tk.SOLID, borderwidth=3 if is_active else 1)
            if not is_active and not self.board_logic.small_boards[i].winner:
                frame.config(bg=self.master.cget('bg')) # reset to default background

# MAIN APPLICATION LOGIC
def launch_selected_game(root: tk.Tk, game_type: str, difficulty: str):
    for widget in root.winfo_children(): widget.destroy()
    title_prefix = "Classic" if game_type == "classic" else "Ultimate"
    root.title(f"{title_prefix} Tic-Tac-Toe - {difficulty.title()} AI")
    (ClassicGameGUI if game_type == "classic" else UltimateGameGUI)(root, difficulty)

def main():
    root = tk.Tk()
    root.title("Tic-Tac-Toe Launcher")
    StartScreen(root, partial(launch_selected_game, root))
    root.mainloop()

if __name__ == "__main__":
    main()