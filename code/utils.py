def _wrap_as_markdown(text: str) -> str:
    """
    Wrap input text into triple single quotes
    :param text: input text
    :return: wrapped text
    """
    return f'```\n{text}\n```'


def _join_text(*texts: str) -> str:
    """
    Join input strings into one string separated by a line break
    :param texts: input strings
    :return: joined string
    """
    return '\n'.join(texts)
