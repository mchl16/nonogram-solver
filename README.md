# nonogram-solver
Nonogram solver written in Python

## How to use
If run with `debug` as parameter, the program reads two integers: `n` and `m`, then `n+m` lines describing constraints for rows and columns. The output will be printed to `stdout`. <br>
Otherwise, the same values will be read from `zad_input.txt` and written to `zad_output.txt`.

## How it works
1. Possible fillings of rows/columns are generated
2. Repeat steps 3 and 4 until solved:
3. For each row/column, those fillings are filtered to see if they may still be valid. Mark each field with a known color as such.
4. If step 3 produces no results, try to backtrack by substituting each filling and removing those that lead to errors.
