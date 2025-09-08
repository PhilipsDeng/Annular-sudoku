# annular_sudoku_all_layers_no_highlight.py
import argparse, math, os, random
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

N = 9
DIGITS = list(range(1, N + 1))

START_RING_OFFSET = 1
SECTORS = [(0,1,2), (3,4,5), (6,7,8)]
LAYERS = 3
LAYER_LEN = 3

def find_empty(grid):
    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                return r, c
    return None

def build_box_map_all_layers():
    box_map = [[-1]*N for _ in range(N)]
    layers_ranges = []
    for li in range(LAYERS):
        r0 = li * LAYER_LEN
        r1 = r0 + LAYER_LEN - 1
        layers_ranges.append((r0, r1))
        for si, cols in enumerate(SECTORS):
            box_id = li * len(SECTORS) + si
            for r in range(r0, r1+1):
                for c in cols:
                    box_map[r][c] = box_id
    return box_map, SECTORS, layers_ranges

def valid(grid, r, c, v, box_map):
    if v in grid[r]:
        return False
    if any(grid[i][c] == v for i in range(N)):
        return False
    bid = box_map[r][c]
    if bid != -1:
        for i in range(N):
            for j in range(N):
                if box_map[i][j] == bid and grid[i][j] == v:
                    return False
    return True

def solve_one(grid, box_map) -> bool:
    pos = find_empty(grid)
    if not pos:
        return True
    r,c = pos
    vals = DIGITS[:]
    random.shuffle(vals)
    for v in vals:
        if valid(grid, r, c, v, box_map):
            grid[r][c] = v
            if solve_one(grid, box_map):
                return True
            grid[r][c] = 0
    return False

def count_solutions(grid, cap=2, box_map=None) -> int:
    cnt = 0
    def backtrack():
        nonlocal cnt
        if cnt >= cap: return
        pos = find_empty(grid)
        if not pos:
            cnt += 1
            return
        r,c = pos
        for v in DIGITS:
            if valid(grid, r, c, v, box_map):
                grid[r][c] = v
                backtrack()
                grid[r][c] = 0
                if cnt >= cap: return
    backtrack()
    return cnt

def generate_full_grid(seed=None, box_map=None):
    if seed is not None: random.seed(seed)
    grid = [[0]*N for _ in range(N)]
    solve_one(grid, box_map)
    return grid

def dig_holes_unique(solution, target_givens=30, max_attempts=4000, seed=None, box_map=None):
    if seed is not None: random.seed(seed)
    puzzle = deepcopy(solution)
    cells = [(r,c) for r in range(N) for c in range(N)]
    random.shuffle(cells)
    givens = N*N
    attempts = 0
    for r,c in cells:
        if givens <= target_givens: break
        if attempts > max_attempts: break
        attempts += 1
        bak = puzzle[r][c]; puzzle[r][c] = 0
        tmp = deepcopy(puzzle)
        if count_solutions(tmp, cap=2, box_map=box_map) == 1:
            givens -= 1
        else:
            puzzle[r][c] = bak
    return puzzle

def draw_annular_sudoku(ax, grid, title=None, font_size=10, start_ring_offset=1):
    R_outer = 1.0
    total_rings = N + start_ring_offset
    rings = [R_outer * (i / total_rings) for i in range(1, total_rings + 1)]
    center_radius = rings[0]
    ax.set_aspect('equal'); ax.axis('off')
    ax.add_artist(plt.Circle((0,0), center_radius, color='black', zorder=10))

    cmap = plt.get_cmap('rainbow')
    for i,r in enumerate(rings):
        col = cmap(i / (len(rings)-1))
        lw = 1.5 if (i+1)%3 != 1 or i==0 else 5.0
        if i != 9:
            ax.add_artist(plt.Circle((0,0), r, fill=False, linewidth=lw, color=col, alpha=0.8, zorder=2))
        else:
            ax.add_artist(plt.Circle((0,0), r, fill=False, linewidth=lw, color='purple', alpha=0.8, zorder=2))
    for j in range(N):
        ang = 2*math.pi*j / N
        x = R_outer * math.cos(ang); y = R_outer * math.sin(ang)
        if j % 3 == 0:
            ax.plot([0,x],[0,y], linewidth=3.0, color='purple', alpha=0.6, zorder=2)
        else:
            ax.plot([0,x],[0,y], linewidth=1.5, color='black', alpha=0.6, zorder=2)

    for r in range(N):
        r_draw = r + start_ring_offset
        r_in = rings[r_draw - 1] if r_draw > 0 else 0.0
        r_out = rings[r_draw]
        r_mid = (r_in + r_out) / 2.0
        for c in range(N):
            a0 = 2*math.pi*c / N; a1 = 2*math.pi*(c+1) / N
            a_mid = (a0 + a1) / 2.0
            val = grid[r][c]
            if val != 0:
                scale = r_mid / 1.0
                ax.text(r_mid*math.cos(a_mid), r_mid*math.sin(a_mid), str(val),
                        ha='center', va='center', fontsize=font_size*(0.8+0.2*scale))
    if title: ax.set_title(title, pad=8)

def save_puzzle_and_solution(puz, sol, idx, out_dir, pdf, font_size=10, dpi=180):
    os.makedirs(out_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8,8))
    draw_annular_sudoku(ax, puz, title=f"Annular Sudoku #{idx}", font_size=font_size,
                        start_ring_offset=START_RING_OFFSET)
    png_p = os.path.join(out_dir, f"annular_{idx}.png")
    fig.savefig(png_p, bbox_inches='tight', dpi=dpi); pdf.savefig(fig, bbox_inches='tight'); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8,8))
    draw_annular_sudoku(ax, sol, title=f"Solution #{idx}", font_size=font_size,
                        start_ring_offset=START_RING_OFFSET)
    png_s = os.path.join(out_dir, f"annular_{idx}_solution.png")
    fig.savefig(png_s, bbox_inches='tight', dpi=dpi); pdf.savefig(fig, bbox_inches='tight'); plt.close(fig)
    return png_p, png_s

def _build_one_puzzle(idx: int, seed: int, givens: int):
    """Worker: build one (puzzle, solution) pair.

    Returns (idx, puzzle, solution). Runs in a separate process for speed.
    """
    # Build local constraints to avoid cross-process state issues
    box_map, _, _ = build_box_map_all_layers()
    # Unique seeds per phase to ensure determinism without cross-talk
    full = generate_full_grid(seed=seed + idx, box_map=box_map)
    puz = dig_holes_unique(full, target_givens=givens, max_attempts=4000,
                           seed=(seed + 100 * idx), box_map=box_map)
    return idx, puz, full

def main():
    parser = argparse.ArgumentParser(description="Annular Sudoku - all layers & sectors enforced (no highlight)")
    parser.add_argument('--count', type=int, default=10, help='number of puzzles')
    parser.add_argument('--givens', type=int, default=35, help='givens per puzzle')
    parser.add_argument('--seed', type=int, default=2025, help='random seed')
    parser.add_argument('--workers', type=int, default=None,
                        help='number of parallel workers (processes), default: CPU count')
    parser.add_argument('--out', type=str, default='annular_out', help='output dir')
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out, exist_ok=True)
    pdf_path = os.path.join(args.out, 'annular_bundle.pdf')

    workers = args.workers or (os.cpu_count() or 1)
    with PdfPages(pdf_path) as pdf:
        indices = list(range(1, args.count + 1))
        if workers <= 1 or args.count == 1:
            for i in indices:
                _, puz, full = _build_one_puzzle(i, args.seed, args.givens)
                save_puzzle_and_solution(puz, full, i, args.out, pdf, font_size=10, dpi=300)
        else:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for (i, puz, full) in ex.map(_build_one_puzzle, indices, repeat(args.seed), repeat(args.givens)):
                    save_puzzle_and_solution(puz, full, i, args.out, pdf, font_size=10, dpi=300)
    print("Done. out:", os.path.abspath(args.out))

if __name__ == '__main__':
    main()
