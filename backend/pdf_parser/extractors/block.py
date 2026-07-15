class BlockExtractor:
    BLOCK_WINDOWS = {
        "points": (555.0, 580.0)  # Traps x0 ~564.0 (the very last column)
    }

    @classmethod
    def extract(cls, words, clean_stat_func) -> int:
        block_text = "."
        blk_min, blk_max = cls.BLOCK_WINDOWS["points"]

        for x0, text in words:
            if blk_min <= x0 <= blk_max:
                block_text = text

        return clean_stat_func(block_text)