def wrap_as_markdown(text: str) -> str:
    return f'```\n{text}\n```'


def join_text(*args: str) -> str:
    return '\n'.join(args)
