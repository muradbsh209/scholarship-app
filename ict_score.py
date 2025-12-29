# ict.py faylı


def calculate_ict_grade():
    print("\n--- İKT Fənni üzrə Qiymətləndirmə ---")
    
    # Hər bir balı 100 üzərindən soruşuruq
    quiz_raw = float(input("Quiz balını daxil edin (0-100): "))
    lab_raw = float(input("Laboratoriya balını daxil edin (0-100): "))
    presentation_raw = float(input("Prezentasiya balını daxil edin (0-100): "))
    
    # Hər birinin 20%-ni hesablayırıq
    quiz_contribution = quiz_raw * 0.20
    lab_contribution = lab_raw * 0.20
    presentation_contribution = presentation_raw * 0.20
    
    # Balları toplayırıq
    total_ict_score = quiz_contribution + lab_contribution + presentation_contribution
    
    print(f"-> İKT üzrə toplanan cəmi bal: {total_ict_score} / 60")
    
    return total_ict_score


def calculate_ict_from_components(quiz_raw, lab_raw, presentation_raw, exam_raw):
    """
    Quiz, lab, prezentasiya (hər biri 20%) + imtahan (40%) = yekun 0-100 bal
    """
    quiz_contribution = quiz_raw * 0.20
    lab_contribution = lab_raw * 0.20
    presentation_contribution = presentation_raw * 0.20
    exam_contribution = exam_raw * 0.40
    return quiz_contribution + lab_contribution + presentation_contribution + exam_contribution