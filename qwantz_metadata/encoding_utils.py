import codecs


def fallback_to_latin1(e: UnicodeError):
    assert isinstance(e, UnicodeEncodeError)
    return e.object[e.start:e.end].encode("latin1"), e.end


codecs.register_error("fallback_to_latin1", fallback_to_latin1)


def fix_encoding(s: str | None) -> str | None:
    if s is None:
        return
    while True:
        try:
            new_s = s.encode("cp1252", errors="fallback_to_latin1").decode("utf-8")
            if new_s == s:
                return s
            s = new_s
        except UnicodeError:
            return s
