class ReceptionExtractor:
    # Traps coordinate ranges specifically for reception stats
    RECEPTION_WINDOWS = {
        "total":     (360.0, 375.0), # Traps x0: 365.8
        "errors":    (376.0, 395.0), # Traps x0: 385.9
        "positive":  (396.0, 420.0), # Traps x0: 403.5
        "excellent": (421.0, 450.0)  # Traps x0: 426.8 and 431.5
    }

    @classmethod
    def extract(cls, words, clean_stat_func) -> tuple[int, int, int, int]:
        """
        Extracts total, errors, positive, and excellent reception counts
        from a single row of words.
        """
        tot_text, err_text, pos_text, exc_text = ".", ".", ".", ""

        tot_min, tot_max = cls.RECEPTION_WINDOWS["total"]
        err_min, err_max = cls.RECEPTION_WINDOWS["errors"]
        pos_min, pos_max = cls.RECEPTION_WINDOWS["positive"]
        exc_min, exc_max = cls.RECEPTION_WINDOWS["excellent"]

        for x0, text in words:
            if tot_min <= x0 <= tot_max:
                tot_text = text
            elif err_min <= x0 <= err_max:
                err_text = text
            elif pos_min <= x0 <= pos_max and "%" in text:
                pos_text = text
            elif exc_min <= x0 <= exc_max:
                cleaned_token = text.replace("(", "").replace(")", "").strip()
                if cleaned_token:
                    exc_text = cleaned_token

        # Clean strings to base integers
        total_receptions = clean_stat_func(tot_text)
        reception_errors = clean_stat_func(err_text)
        pos_percent = clean_stat_func(pos_text)
        exc_percent = clean_stat_func(exc_text)

        # Calculate raw counts
        positive_receptions = 0
        excellent_receptions = 0

        if total_receptions > 0:
            positive_receptions = round((pos_percent * total_receptions) / 100)
            excellent_receptions = round((exc_percent * total_receptions) / 100)

        return (total_receptions, reception_errors, positive_receptions, excellent_receptions)