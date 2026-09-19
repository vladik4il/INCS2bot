from copy import copy

from pyrogram.types import MessageEntity


def correct_message_entities(entities: list[MessageEntity] | None,
                             original_text: str, new_text: str) -> list[MessageEntity] | None:
    """Correct message entities (a.k.a. Markdown formatting) for edited text."""

    if entities is None:
        return

    length_diff = len(original_text) - len(new_text)

    new_entities = []
    for i, entity in enumerate(entities):
        entity = copy(entity)
        entity.offset -= length_diff

        if entity.offset >= 0:
            new_entities.append(entity)

    return new_entities