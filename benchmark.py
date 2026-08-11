import timeit
import re

content = """[package]
name = "test"
version = "1.0.0"

[source]
url = "http://example.com"
sha256 = "1234"

[bottle.macos-arm64]
url = "http://example.com/bottle1"
sha256 = "abcd"

[bottle.linux-x86_64]
url = "http://example.com/bottle2"
sha256 = "efgh"

[build]
commands = ["make"]
"""

setup_unoptimized = """
import re
content = %r
""" % content

stmt_unoptimized = """
last_bottle_end = -1
for m in re.finditer(
    r'\\[bottle\\.[^\\]]+\\][ \\t]*\\n'
    r'url[ \\t]*=[ \\t]*"[^"]*"[ \\t]*\\n'
    r'sha256[ \\t]*=[ \\t]*"[^"]*"[ \\t]*\\n',
    content,
):
    last_bottle_end = m.end()
"""

setup_optimized = """
import re
content = %r
BOTTLE_SECTION_PATTERN = re.compile(
    r'\\[bottle\\.[^\\]]+\\][ \\t]*\\n'
    r'url[ \\t]*=[ \\t]*"[^"]*"[ \\t]*\\n'
    r'sha256[ \\t]*=[ \\t]*"[^"]*"[ \\t]*\\n'
)
""" % content

stmt_optimized = """
last_bottle_end = -1
for m in BOTTLE_SECTION_PATTERN.finditer(content):
    last_bottle_end = m.end()
"""

if __name__ == '__main__':
    n = 100000
    unopt_time = timeit.timeit(stmt_unoptimized, setup=setup_unoptimized, number=n)
    opt_time = timeit.timeit(stmt_optimized, setup=setup_optimized, number=n)

    print(f"Unoptimized time: {unopt_time:.6f}s")
    print(f"Optimized time:   {opt_time:.6f}s")
    if unopt_time > 0:
        improvement = (unopt_time - opt_time) / unopt_time * 100
        print(f"Improvement:      {improvement:.2f}%")
