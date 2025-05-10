import re


def get_words_from_line(line: str) -> list[str]:
    if line[0] == '〚':
        return []
    line_text = line.split(': ', 1)[1].lower()
    line_text = re.sub(r"〚[^〛]*〛", "", line_text)
    line_text = re.sub(r"\w*⦃[^⦄]*⦄\w*", "", line_text)
    line_text = re.sub(r"\w*…\w*", "", line_text)
    return re.findall(r"\w+", line_text) + re.findall(r"\w+(-\w+)+", line_text)


def strip_line(line: str) -> str:
    if line[0] == '〚':
        return ""
    line_text = line.split(': ', 1)[1]
    line_text = re.sub(r"〚[^〛]*〛", " ", line_text)
    line_text = re.sub(r"⦃[^⦄]*⦄", " ", line_text)
    line_text = re.sub(r"[▹◃◖◗]", " ", line_text)
    line_text = line_text.replace("…", " ")
    return line_text
