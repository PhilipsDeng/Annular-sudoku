# Annular Sudoku

A simple Sudoku generator and solver. It can create Sudoku puzzles, solve them, and export results to PDF.
## Usage
This command generates **5 Sudoku puzzles** and saves them into `example/output.pdf`.
<pre class="overflow-visible!" data-start="89" data-end="299"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-markdown"><span><span>
python annular_gen.py --out example --count 5
</span></span></code></div></div></pre>



## Examples

Check the `example/` folder for sample outputs:

* `example/output.pdf` – multiple Sudoku puzzles
* `example/sudoku_1.png` – a single Sudoku puzzle
* `example/sudoku_1_solution.png` – the corresponding solution

## Requirements

* Python 3.8+
* matplotlib

Install dependencies:

<pre class="overflow-visible!" data-start="691" data-end="734"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>pip install -r requirements.txt
</span></span></code></div></div></pre>

## License

MIT
