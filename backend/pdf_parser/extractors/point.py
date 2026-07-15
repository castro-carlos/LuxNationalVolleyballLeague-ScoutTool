class PointsExtractor:
    POINTS_WINDOWS = {
        "total":      (230.0, 250.0), # Traps x0 ~238.3
        "break":      (251.0, 270.0), # Traps x0 ~260.6
        "plus_minus": (271.0, 290.0)  # Traps x0 ~273.2
    }

    @classmethod
    def extract(cls, words, clean_stat_func) -> tuple[int, int, int]:
        tot_text, bp_text, pm_text = ".", ".", "."

        tot_min, tot_max = cls.POINTS_WINDOWS["total"]
        bp_min, bp_max = cls.POINTS_WINDOWS["break"]
        pm_min, pm_max = cls.POINTS_WINDOWS["plus_minus"]

        for x0, text in words:
            if tot_min <= x0 <= tot_max:
                tot_text = text
            elif bp_min <= x0 <= bp_max:
                bp_text = text
            elif pm_min <= x0 <= pm_max:
                pm_text = text

        # Plus-minus can contain positive "+" signs, which we need to strip cleanly
        cleaned_pm_text = pm_text.replace("+", "").strip()

        # Handle negative signs cleanly if they exist
        try:
            pm_val = int(cleaned_pm_text) if cleaned_pm_text and cleaned_pm_text != "." else 0
        except ValueError:
            pm_val = 0

        return (
            clean_stat_func(tot_text),
            clean_stat_func(bp_text),
            pm_val
        )