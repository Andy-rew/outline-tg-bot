def _wrap_as_markdown(text: str) -> str:
    return f'```\n{text}\n```'


def _join_text(*args: str) -> str:
    return '\n'.join(args)
