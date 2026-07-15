class ServiceExtractor:
    # Service coordinate windows mapped from Weber Steve's coordinate data
    SERVICE_WINDOWS = {
        "total":  (295.0, 315.0),  # Catches x0: 303.1
        "errors": (316.0, 335.0),  # Catches x0: 323.2
        "aces":   (336.0, 355.0)   # Catches x0: 343.5
    }

    @classmethod
    def extract(cls, row_words, clean_stat_func) -> tuple[int, int, int]:
        """
        Scans words for service metrics using coordinate windows.
        """
        tot_text, err_text, ace_text = ".", ".", "."

        tot_min, tot_max = cls.SERVICE_WINDOWS["total"]
        err_min, err_max = cls.SERVICE_WINDOWS["errors"]
        ace_min, ace_max = cls.SERVICE_WINDOWS["aces"]

        for x0, text in row_words:
            if tot_min <= x0 <= tot_max:
                tot_text = text
            elif err_min <= x0 <= err_max:
                err_text = text
            elif ace_min <= x0 <= ace_max:
                ace_text = text

        return (
            clean_stat_func(tot_text),
            clean_stat_func(err_text),
            clean_stat_func(ace_text)
        )