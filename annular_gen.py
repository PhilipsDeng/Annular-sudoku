import argparse
import math
import os
import random
from copy import deepcopy
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

N = 9
DIGITS = list(range(1, N + 1))

def find_empty(grid):
    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                return r, c
    return None

def valid(grid, r, c, v):
    if v in grid[r]:            
        return False
    if any(grid[i][c] == v for i in range(N)):  
        return False
    br = (r // 3) * 3           
    bc = (c // 3) * 3
    for i in range(3):
        for j in range(3):
            if grid[br + i][bc + j] == v:
                return False
    return True

def solve_one(grid) -> bool:
    """Backtracking solver (finds one solution)."""
    pos = find_empty(grid)
    if not pos:
        return True
    r, c = pos
    vals = DIGITS[:]
    random.shuffle(vals)
    for v in vals:
        if valid(grid, r, c, v):
            grid[r][c] = v
            if solve_one(grid):
                return True
            grid[r][c] = 0
    return False

def count_solutions(grid, cap=2) -> int:
    """Count number of solutions (stop at cap)."""
    cnt = 0
    def backtrack():
        nonlocal cnt
        if cnt >= cap:
            return
        pos = find_empty(grid)
        if not pos:
            cnt += 1
            return
        r, c = pos
        for v in DIGITS:
            if valid(grid, r, c, v):
                grid[r][c] = v
                backtrack()
                grid[r][c] = 0
                if cnt >= cap:
                    return
    backtrack()
    return cnt

def generate_full_grid(seed=None):
    if seed is not None:
        random.seed(seed)
    grid = [[0] * N for _ in range(N)]
    solve_one(grid)
    return grid

def dig_holes_unique(solution, target_givens=30, max_attempts=4000, seed=None):
    """Remove digits while keeping uniqueness."""
    if seed is not None:
        random.seed(seed)
    puzzle = deepcopy(solution)
    cells = [(r, c) for r in range(N) for c in range(N)]
    random.shuffle(cells)
    givens = N * N
    attempts = 0
    for r, c in cells:
        if givens <= target_givens:
            break
        if attempts > max_attempts:
            break
        attempts += 1
        bak = puzzle[r][c]
        puzzle[r][c] = 0
        tmp = deepcopy(puzzle)
        if count_solutions(tmp, cap=2) == 1:
            givens -= 1
        else:
            puzzle[r][c] = bak
    return puzzle

def draw_annular_sudoku(ax, grid, title=None, font_size=10, show_numbers=True):
    R_outer = 1.0
    rings = [R_outer * (i / N) for i in range(1, N + 1)]
    center_radius = rings[0]   
    ax.set_aspect('equal')
    ax.axis('off')
    ax.add_artist(plt.Circle((0, 0), center_radius, color='black'))

    # rainbow concentric rings
    cmap = plt.get_cmap('rainbow')
    for i, r in enumerate(rings):
        col = cmap(i / (len(rings) - 1))  
        lw  = 1.5 if (i + 1) % 3 != 0 else 5.0
        circle = plt.Circle((0, 0), r, fill=False, linewidth=lw, color=col)
        ax.add_artist(circle)

    # radial lines (red every 3rd)
    for j in range(N):
        ang = 2 * math.pi * j / N
        x = R_outer * math.cos(ang)
        y = R_outer * math.sin(ang)
        if j % 3 == 0:
            ax.plot([0, x], [0, y], linewidth=3.0, color='red')
        else:
            ax.plot([0, x], [0, y], linewidth=1.5, color='black')

    # draw numbers
    if show_numbers:
        for r in range(N):
            if r == 0:
                continue
            r_in = rings[r - 1] if r > 0 else 0.0
            r_out = rings[r]
            r_mid = (r_in + r_out) / 2.0
            for c in range(N):
                a0 = 2 * math.pi * c / N
                a1 = 2 * math.pi * (c + 1) / N
                a_mid = (a0 + a1) / 2.0
                val = grid[r][c]
                if val != 0:
                    scale = r_mid / 1.0
                    ax.text(r_mid * math.cos(a_mid),
                            r_mid * math.sin(a_mid),
                            str(val),
                            ha='center', va='center',
                            fontsize=font_size * (0.6 + 0.4 * scale))
    if title:
        ax.set_title(title, pad=8)

def save_puzzle_and_solution(puz, sol, idx, out_dir, pdf, font_size=10, dpi=180):
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))
    draw_annular_sudoku(ax, puz, title=f"Annular Sudoku #{idx}", font_size=font_size, show_numbers=True)
    png_p = os.path.join(out_dir, f"annular_{idx}.png")
    fig.savefig(png_p, bbox_inches='tight', dpi=dpi)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8))
    draw_annular_sudoku(ax, sol, title=f"Solution #{idx}", font_size=font_size, show_numbers=True)
    png_s = os.path.join(out_dir, f"annular_{idx}_solution.png")
    fig.savefig(png_s, bbox_inches='tight', dpi=dpi)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
    return png_p, png_s

def main():
    parser = argparse.ArgumentParser(description="Generate annular sudoku PNG + PDF")
    parser.add_argument('--count', type=int, default=5, help='number of puzzles')
    parser.add_argument('--givens', type=int, default=35, help='givens per puzzle')
    parser.add_argument('--font', type=float, default=10, help='font size')
    parser.add_argument('--dpi', type=int, default=300, help='image DPI')
    parser.add_argument('--seed', type=int, default=2025, help='random seed')
    parser.add_argument('--out', type=str, default='annular_out', help='output dir')
    args = parser.parse_args()

    random.seed(args.seed)
    pdf_path = os.path.join(args.out, 'annular_bundle.pdf')
    os.makedirs(args.out, exist_ok=True)

    with PdfPages(pdf_path) as pdf:
        for i in range(1, args.count + 1):
            full = generate_full_grid(seed=args.seed + i)
            puz = dig_holes_unique(full, target_givens=args.givens,
                                   max_attempts=4000, seed=(args.seed + 100 * i))
            save_puzzle_and_solution(puz, full, i, args.out, pdf,
                                     font_size=args.font, dpi=args.dpi)
    print(f"Done! Output in {os.path.abspath(args.out)}")
    print(f"- PDF: {os.path.abspath(pdf_path)}")

if __name__ == '__main__':
    main()
