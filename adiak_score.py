def calculate_adiak_grade():
    print("\n--- ADIAK Fənni üzrə Qiymətləndirmə (Düzəldilmiş) ---")
    
    # 1. Pre-exam hissəsi (Cəmi 55 bal)
    # Presentation birbaşa 15 bal
    presentation = float(input("Presentation balını daxil edin (0-100): "))
    
    # Aktivlik birbaşa 20 bal
    participation = float(input("Aktivlik (Participation) balını daxil edin (0-100): "))
    
    # Midterm imtahanının 20%-i (Maksimum 20 bal)
    midterm_raw = float(input("Midterm imtahan nəticəsini daxil edin (0-100): "))
    midterm_contribution = midterm_raw * 0.20 
    
    pre_exam_total = presentation * 0.15 + participation * 0.2 + midterm_contribution * 0.2
    print(f"-> İmtahana qədər toplanan cəmi bal (Pre-exam): {pre_exam_total} / 55.00")
    
    # 2. Final imtahanı (Cəmi 45 bal)
    # Final imtahanının 45%-i
    final_raw = float(input("Final imtahan nəticəsini daxil edin (0-100): "))
    final_contribution = final_raw * 0.45 

    
    print(f"-> Final imtahanından gələn bal: {final_contribution} / 45.00")
    
    # Yekun Nəticə (Pre 55 + Final 45 = 100)
    total_score = pre_exam_total + final_contribution
    
    return total_score


def calculate_adiak_from_components(presentation, participation, midterm_raw, final_raw):
    """
    Formdan gələn komponentlərə əsasən ADIAK yekun balını hesablayır
    """
    midterm_contribution = midterm_raw * 0.20
    pre_exam_total = presentation * 0.15 + participation * 0.2 + midterm_contribution * 0.2
    final_contribution = final_raw * 0.45
    return pre_exam_total + final_contribution