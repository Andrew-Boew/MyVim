from typing import Any, Tuple


class WordNavigator:
    @staticmethod
    def _to_string(target: Any) -> str:
        if hasattr(target, "c_str"):
            return target.c_str()
        return str(target)

    @classmethod
    def find_word_end(cls, target: Any, from_col: int) -> int:
        text = cls._to_string(target)
        length = len(text)
        if length == 0:
            return 0
        if from_col >= length - 1:
            return max(0, length - 1)

        idx = from_col
        if not text[idx].isspace():
            is_alnum = text[idx].isalnum()
            end_current = idx
            while (
                end_current + 1 < length
                and not text[end_current + 1].isspace()
                and text[end_current + 1].isalnum() == is_alnum
            ):
                end_current += 1
            if idx < end_current:
                return end_current
            idx = end_current + 1

        while idx < length and text[idx].isspace():
            idx += 1

        if idx >= length:
            return length - 1

        next_alnum = text[idx].isalnum()
        end_next = idx
        while (
            end_next + 1 < length
            and not text[end_next + 1].isspace()
            and text[end_next + 1].isalnum() == next_alnum
        ):
            end_next += 1

        return end_next

    @classmethod
    def find_word_start(cls, target: Any, from_col: int) -> int:
        text = cls._to_string(target)
        length = len(text)
        if length == 0 or from_col <= 0:
            return 0

        idx = min(from_col, length - 1)
        if not text[idx].isspace():
            is_alnum = text[idx].isalnum()
            start_current = idx
            while (
                start_current > 0
                and not text[start_current - 1].isspace()
                and text[start_current - 1].isalnum() == is_alnum
            ):
                start_current -= 1
            if start_current < idx:
                return start_current
            idx = start_current - 1

        while idx >= 0 and text[idx].isspace():
            idx -= 1

        if idx <= 0:
            return 0

        prev_alnum = text[idx].isalnum()
        start_prev = idx
        while (
            start_prev > 0
            and not text[start_prev - 1].isspace()
            and text[start_prev - 1].isalnum() == prev_alnum
        ):
            start_prev -= 1

        return start_prev

    @classmethod
    def get_word_range_at(cls, target: Any, col: int) -> Tuple[int, int]:
        text = cls._to_string(target)
        length = len(text)
        if length == 0 or col < 0 or col >= length:
            return 0, 0

        start = col
        is_alnum = text[col].isalnum()
        is_space = text[col].isspace()

        while start > 0:
            prev = text[start - 1]
            if is_space:
                if not prev.isspace():
                    break
            else:
                if prev.isspace() or prev.isalnum() != is_alnum:
                    break
            start -= 1

        end = col
        while end < length:
            curr = text[end]
            if is_space:
                if not curr.isspace():
                    break
            else:
                if curr.isspace() or curr.isalnum() != is_alnum:
                    break
            end += 1

        while end < length and text[end].isspace():
            end += 1

        return start, end
