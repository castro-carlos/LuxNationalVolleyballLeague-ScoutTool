class AttackExtractor:
    ATTACK_WINDOWS = {
        "total":   (450.0, 470.0), # Traps x0 ~457.7
        "errors":  (471.0, 490.0), # Traps x0 ~479.7
        "blocked": (491.0, 510.0), # Traps x0 ~499.5
        "kills":   (511.0, 530.0)  # Traps x0 ~520.4
    }

    @classmethod
    def extract(cls, words, clean_stat_func) -> tuple[int, int, int, int]:
        tot_text, err_text, blk_text, kill_text = ".", ".", ".", "."

        tot_min, tot_max = cls.ATTACK_WINDOWS["total"]
        err_min, err_max = cls.ATTACK_WINDOWS["errors"]
        blk_min, blk_max = cls.ATTACK_WINDOWS["blocked"]
        kill_min, kill_max = cls.ATTACK_WINDOWS["kills"]

        for x0, text in words:
            if tot_min <= x0 <= tot_max:
                tot_text = text
            elif err_min <= x0 <= err_max:
                err_text = text
            elif blk_min <= x0 <= blk_max:
                blk_text = text
            elif kill_min <= x0 <= kill_max:
                kill_text = text

        return (
            clean_stat_func(tot_text),
            clean_stat_func(err_text),
            clean_stat_func(blk_text),
            clean_stat_func(kill_text)
        )