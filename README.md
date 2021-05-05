# Coversheet Adder
Coversheet Adder for Exams.

**Instructions**:
* Create directories `/Input` and `/Output`.

* Scan your script by question and save it as a pdf with the naming convention `{MODULE_CODE} Q{Number}` and save to the `/Input` Folder.

* Example Usage on Command Line (In the same directory as `covadd.py`)
```python3 covadd.py by_q 01701234 MATH50001 6```

* Example Usage with Python (e.g. Notebook in same directory as `covadd.py`)
```
import covadd
covadd.by_question("01701234", "MATH50001", 6)
```

* Formatted files will be found in `/Output`.
