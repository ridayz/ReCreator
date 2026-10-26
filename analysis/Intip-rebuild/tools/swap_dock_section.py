path = r"H:\Default Project\analysis\Intip-rebuild\mockup\compare.html"
src = open(path, encoding="utf-8").read()

start = src.find("<h2>2b")
end = src.find("<h2>3 ")
assert 0 < start < end, (start, end)

newblock = open(
    r"H:\Default Project\analysis\Intip-rebuild\tools\dock_section.html",
    encoding="utf-8",
).read()

src = src[:start] + newblock + src[end:]
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
print("replaced dock section; div balanced:", src.count("<div") == src.count("</div>"))
