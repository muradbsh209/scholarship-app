def calculate_history_grade():
    print("\n--- Tarix Fənni üzrə Qiymətləndirmə ---")
    
    # Tarix balını birbaşa soruşuruq
    history_point = float(input("Tarix balını daxil edin (0-100): "))
    
    return history_point


def calculate_history_from_components(seminar, interactive, presentation, midterm, final):
    """
    Seminar 10%, interaktiv mühazirə 5%, təqdimat 5%, midterm 20%, final 60%
    Hamısı 0-100 arası qəbul olunur və yekunda 0-100 bal qaytarılır.
    """
    return (
        seminar * 0.10
        + interactive * 0.05
        + presentation * 0.05
        + midterm * 0.20
        + final * 0.60
    )