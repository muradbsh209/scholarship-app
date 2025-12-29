def calculate_english_grade():
    print("\n--- İngilis Dili üzrə Qiymətləndirmə ---")
    
    # 1. Pre-exam (Cəmi 50%)
    assessment = float(input("Assessment Test balını daxil edin (0-100): "))
    writing = float(input("Graded Writing balını daxil edin (0-100): "))
    
    print("3 Presentation balını daxil edin:")
    p1 = float(input("1-ci Presentation: "))
    p2 = float(input("2-ci Presentation: "))
    p3 = float(input("3-cü Presentation: "))
    pres_avg = (p1 + p2 + p3) / 3
    
    participation = float(input("Participation (Dərsdə iştirak) balını daxil edin (0-100): "))
    
    # Pre-exam hesablama: (Bal * Faiz/100)
    # Assessment(20%) + Writing(10%) + Pres_Avg(10%) + Participation(10%) = 50%
    pre_exam_total = (assessment * 0.20) + (writing * 0.10) + (pres_avg * 0.10) + (participation * 0.10)
    
    # 2. After-exam (Midterm/Final - 50%)
    midterm = float(input("Midterm imtahan balını daxil edin (0-100): "))
    after_exam_total = midterm * 0.50
    
    # Yekun 100 ballıq sistem
    final_score = pre_exam_total + after_exam_total
    
    return final_score


def calculate_english_from_components(assessment, writing, p1, p2, p3, participation, midterm):
    """
    Formdan gələn komponentlərə əsasən İngilis dili yekun balını hesablayır
    """
    pres_avg = (p1 + p2 + p3) / 3
    pre_exam_total = (assessment * 0.20) + (writing * 0.10) + (pres_avg * 0.10) + (participation * 0.10)
    after_exam_total = midterm * 0.50
    return pre_exam_total + after_exam_total