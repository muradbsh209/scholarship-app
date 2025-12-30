from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import csv
import io
import re
from adiak_score import calculate_adiak_from_components
from english_score import calculate_english_from_components
from ict_score import calculate_ict_from_components
from history_score import calculate_history_from_components

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-change-in-production"
db = SQLAlchemy(app)

# Admin username
ADMIN_USERNAME = "Root@Sudo;Verba"

# Ixtisas qrupları
qrup_1_RI = [250104, 250108, 250107, 250103, 250110]  # English, ADIAK, ICT
qrup_1_RK = [250101, 250102]  # English, History, ICT
qrup_2 = [250109, 250111]  # English, History, ICT

# İxtisas planları (free, payable)
IXTISAS_PLANS = {
    250104: {"name": "IT", "free": 20, "payable": 10},
    250108: {"name": "CE", "free": 20, "payable": 30},
    250107: {"name": "CS", "free": 20, "payable": 30},
    250103: {"name": "PAM", "free": 30, "payable": 20},
    250110: {"name": "DA", "free": 20, "payable": 10},
    250102: {"name": "CE", "free": 50, "payable": 50},
    250101: {"name": "PE", "free": 30, "payable": 30},
    250109: {"name": "Finance", "free": 20, "payable": 30},
    250111: {"name": "BM", "free": 20, "payable": 30}
}

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ixtisas_id = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)

    english_point = db.Column(db.Float, nullable=False)
    adiak_point = db.Column(db.Float, default=0)
    history_point = db.Column(db.Float, default=0)
    ict_point = db.Column(db.Float, nullable=False)

    average_score = db.Column(db.Float, default=0)
    scholarship_type = db.Column(db.String(50))
    rank = db.Column(db.Integer)

    english_grade = db.Column(db.String(2))
    adiak_grade = db.Column(db.String(2))
    history_grade = db.Column(db.String(2))
    ict_grade = db.Column(db.String(2))
    cancelled = db.Column(db.Boolean, default=False)

    def __init__(self, ixtisas_id, name, surname, english_point, adiak_point, ict_point, history_point=0):
        self.ixtisas_id = int(ixtisas_id)
        self.name = name
        self.surname = surname
        self.english_point = float(english_point)
        self.adiak_point = float(adiak_point) if adiak_point else 0
        self.history_point = float(history_point) if history_point else 0
        self.ict_point = float(ict_point)

        # Meta məlumatlar
        self.scholarship_type = None
        self.rank = None

        # Qiymətləndirmə ilə bağlı sahələr
        self.english_grade = None
        self.adiak_grade = None
        self.history_grade = None
        self.ict_grade = None
        self.cancelled = False  # Hər hansı fəndən D və ya aşağı alıbsa

        self.average_score = self.calculate_average()
        self._calculate_grades_and_status()

    def calculate_average(self):
        """3 fənnin orta balını hesablayır"""
        if self.ixtisas_id in qrup_1_RI:
            # English, ADIAK, ICT
            return (self.english_point + self.adiak_point + self.ict_point) / 3
        elif self.ixtisas_id in qrup_1_RK or self.ixtisas_id in qrup_2:
            # English, History, ICT
            return (self.english_point + self.history_point + self.ict_point) / 3
        return 0

    @staticmethod
    def _grade_english(score: float) -> str:
        """İngilis dili üçün A/B/C/D/F hesablanması"""
        if score >= 70:
            return "A"
        if 60 <= score <= 69:
            return "B"
        if 50 <= score <= 59:
            return "C"
        if 40 <= score <= 49:
            return "D"
        return "F"

    @staticmethod
    def _grade_other(score: float) -> str:
        """Digər fənlər (ADIAK, Tarix, ICT) üçün A/B/C/D/F hesablanması"""
        if 91 <= score <= 100:
            return "A"
        if 81 <= score < 91:
            return "B"
        if 71 <= score < 81:
            return "C"
        if 61 <= score < 71:
            return "D"
        return "F"

    def _calculate_grades_and_status(self):
        """Hər fənnin hərf qiymətini və ləğv olunma statusunu hesablayır"""
        self.english_grade = self._grade_english(self.english_point)
        self.ict_grade = self._grade_other(self.ict_point)

        if self.ixtisas_id in qrup_1_RI:
            self.adiak_grade = self._grade_other(self.adiak_point)
            self.history_grade = None
        else:
            self.history_grade = self._grade_other(self.history_point)
            self.adiak_grade = None

        grades = [self.english_grade, self.ict_grade]
        if self.adiak_grade is not None:
            grades.append(self.adiak_grade)
        if self.history_grade is not None:
            grades.append(self.history_grade)

        # Əgər hər hansı fəndən D və ya F alıbsa - ləğv olunur və təqaüd almayacaq
        self.cancelled = any(g in ("D", "F") for g in grades)

    def get_subjects(self):
        """Hansı fənləri oxuduğunu qaytarır"""
        if self.ixtisas_id in qrup_1_RI:
            return ["İngilis dili", "ADIAK", "ICT"]
        elif self.ixtisas_id in qrup_1_RK or self.ixtisas_id in qrup_2:
            return ["İngilis dili", "Tarix", "ICT"]
        return []

    def to_dict(self):
        """Student obyektini dictionary-ə çevirir"""
        return {
            "ixtisas_id": self.ixtisas_id,
            "name": self.name,
            "surname": self.surname,
            "english_point": self.english_point,
            "adiak_point": self.adiak_point,
            "history_point": self.history_point,
            "ict_point": self.ict_point,
            "average_score": round(self.average_score, 2),
            "scholarship_type": self.scholarship_type,
            "rank": self.rank,
            "ixtisas_name": IXTISAS_PLANS.get(self.ixtisas_id, {}).get("name", "Unknown"),
            "english_grade": self.english_grade,
            "adiak_grade": self.adiak_grade,
            "history_grade": self.history_grade,
            "ict_grade": self.ict_grade,
            "cancelled": self.cancelled,
        }


def assign_scholarships():
    """Tələbələri ixtisas_id-yə görə qruplaşdırır, sıralayır və təqaüd verir"""
    # Bütün tələbələri ixtisas_id-yə görə qruplaşdır
    students_by_ixtisas = {}
    all_students = Student.query.all()
    for student in all_students:
        ixtisas_id = student.ixtisas_id
        if ixtisas_id not in students_by_ixtisas:
            students_by_ixtisas[ixtisas_id] = []
        students_by_ixtisas[ixtisas_id].append(student)
    
    # Hər ixtisas üçün tələbələri orta bala görə sırala (yüksəkdən aşağıya)
    for ixtisas_id, ixtisas_students in students_by_ixtisas.items():
        ixtisas_students.sort(key=lambda s: s.average_score, reverse=True)
        
        # Plan məlumatlarını al
        plan = IXTISAS_PLANS.get(ixtisas_id, {"free": 0, "payable": 0})
        free_slots = plan["free"]
        
        # İlk free_slots sayda tələbəyə təqaüd ver
        for idx, student in enumerate(ixtisas_students):
            student.rank = idx + 1
            # Default: təqaüd yoxdur
            student.scholarship_type = None

            # Əgər free slot daxilində deyilsə - təqaüd yoxdur
            if idx >= free_slots:
                continue

            # Əgər hər hansı fəndən D və ya F alıbsa - ləğv olunub, təqaüd YOXDUR
            if student.cancelled:
                continue

            # Bu tələbənin üç fənn üzrə hərf qiymətlərini götür
            if ixtisas_id in qrup_1_RI:
                grades = [student.english_grade, student.adiak_grade, student.ict_grade]
            else:
                grades = [student.english_grade, student.history_grade, student.ict_grade]

            # Təhlükəsizlik üçün, yenə də D və ya F varsa, təqaüd vermirik
            if any(g in ("D", "F") for g in grades):
                continue

            # Elaci: bütün 3 fənn A-dır
            if all(g == "A" for g in grades):
                student.scholarship_type = "Əlaçı təqaüdü"
                continue

            # Zerbeci: 1 və ya 2 A var, qalanları yalnız B və ya C
            num_a = grades.count("A")
            if 1 <= num_a <= 2 and all(g in ("A", "B", "C") for g in grades):
                student.scholarship_type = "Zərbəçi"
                continue

            # Adi təqaüd: heç bir A yoxdur, yalnız B və C
            if num_a == 0 and all(g in ("B", "C") for g in grades):
                student.scholarship_type = "Adi təqaüd"

    db.session.commit()


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        if session.get('username') != ADMIN_USERNAME:
            flash('Bu səhifəyə giriş üçün icazəniz yoxdur.', 'error')
            return redirect(url_for('calculate'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    # If already logged in, redirect to appropriate page
    if 'username' in session:
        if session.get('username') == ADMIN_USERNAME:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('calculate'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            if username == ADMIN_USERNAME:
                return redirect(url_for('index'))
            else:
                return redirect(url_for('calculate'))
        else:
            return render_template('login.html', error='İstifadəçi adı daxil edin')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/')
@admin_required
def index():
    """Ana səhifə - tələbə əlavə etmə formu"""
    all_students = Student.query.all()
    return render_template('index.html', ixtisas_plans=IXTISAS_PLANS, students=all_students)


@app.route('/add_student', methods=['POST'])
@admin_required
def add_student():
    """Yeni tələbə əlavə edir"""
    try:
        ixtisas_id = int(request.form.get('ixtisas_id'))
        name = request.form.get('name')
        surname = request.form.get('surname')

        # İngilis dili komponentləri
        eng_assessment = float(request.form.get('eng_assessment'))
        eng_writing = float(request.form.get('eng_writing'))
        eng_p1 = float(request.form.get('eng_p1'))
        eng_p2 = float(request.form.get('eng_p2'))
        eng_p3 = float(request.form.get('eng_p3'))
        eng_participation = float(request.form.get('eng_participation'))
        eng_midterm = float(request.form.get('eng_midterm'))
        english_point = calculate_english_from_components(
            eng_assessment, eng_writing, eng_p1, eng_p2, eng_p3, eng_participation, eng_midterm
        )

        # İKT komponentləri
        ict_quiz = float(request.form.get('ict_quiz'))
        ict_lab = float(request.form.get('ict_lab'))
        ict_presentation = float(request.form.get('ict_presentation'))
        ict_exam = float(request.form.get('ict_exam'))
        ict_point = calculate_ict_from_components(ict_quiz, ict_lab, ict_presentation, ict_exam)

        # İxtisas_id-yə görə 3-cü fənnin komponentləri
        adiak_point = 0
        history_point = 0

        if ixtisas_id in qrup_1_RI:
            adiak_presentation = float(request.form.get('adiak_presentation'))
            adiak_participation = float(request.form.get('adiak_participation'))
            adiak_midterm = float(request.form.get('adiak_midterm'))
            adiak_final = float(request.form.get('adiak_final'))
            adiak_point = calculate_adiak_from_components(
                adiak_presentation, adiak_participation, adiak_midterm, adiak_final
            )
        elif ixtisas_id in qrup_1_RK or ixtisas_id in qrup_2:
            history_seminar = float(request.form.get('history_seminar'))
            history_interactive = float(request.form.get('history_interactive'))
            history_presentation = float(request.form.get('history_presentation'))
            history_midterm = float(request.form.get('history_midterm'))
            history_final = float(request.form.get('history_final'))
            history_point = calculate_history_from_components(
                history_seminar,
                history_interactive,
                history_presentation,
                history_midterm,
                history_final,
            )
        
        # Yeni tələbə yarat
        student = Student(ixtisas_id, name, surname, english_point, adiak_point, ict_point, history_point)
        db.session.add(student)
        db.session.commit()
        
        return redirect(url_for('index'))
    except Exception as e:
        return f"Xəta: {str(e)}", 400


@app.route('/calculate')
@login_required
def calculate():
    """Təqaüdləri hesabla və nəticələri göstər"""
    assign_scholarships()
    
    # Tələbələri ixtisas_id-yə görə qruplaşdır
    students_by_ixtisas = {}
    all_students = Student.query.all()
    for student in all_students:
        ixtisas_id = student.ixtisas_id
        if ixtisas_id not in students_by_ixtisas:
            students_by_ixtisas[ixtisas_id] = []
        students_by_ixtisas[ixtisas_id].append(student)
    
    # Hər ixtisas üçün tələbələri rank-a görə artan sırada sırala
    for ixtisas_id in students_by_ixtisas:
        students_by_ixtisas[ixtisas_id].sort(key=lambda s: s.rank if s.rank is not None else float('inf'))
    
    # Yalnız təqaüd alan tələbələri göstər
    scholarship_students = [s for s in all_students if s.scholarship_type is not None]
    
    return render_template('results.html', 
                         students_by_ixtisas=students_by_ixtisas,
                         scholarship_students=scholarship_students,
                         ixtisas_plans=IXTISAS_PLANS,
                         students=all_students)


@app.route('/students')
@admin_required
def view_students():
    """Bütün tələbələri göstər"""
    all_students = Student.query.all()
    return render_template('students.html', students=all_students, ixtisas_plans=IXTISAS_PLANS)


@app.route('/clear', methods=['POST'])
@admin_required
def clear_students():
    """Bütün tələbələri sil"""
    Student.query.delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/remove_student/<int:student_id>', methods=['POST'])
@admin_required
def remove_student(student_id):
    """Tək tələbəni sil"""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('view_students'))


@app.route('/edit_student/<int:student_id>', methods=['GET'])
@admin_required
def edit_student(student_id):
    """Tələbə redaktə etmə səhifəsi"""
    student = Student.query.get_or_404(student_id)
    return render_template('edit_student.html', student=student, ixtisas_plans=IXTISAS_PLANS)


@app.route('/update_student/<int:student_id>', methods=['POST'])
@admin_required
def update_student(student_id):
    """Tələbə məlumatlarını yenilə"""
    try:
        student = Student.query.get_or_404(student_id)
        
        ixtisas_id = int(request.form.get('ixtisas_id'))
        name = request.form.get('name')
        surname = request.form.get('surname')

        # İngilis dili komponentləri
        eng_assessment = float(request.form.get('eng_assessment'))
        eng_writing = float(request.form.get('eng_writing'))
        eng_p1 = float(request.form.get('eng_p1'))
        eng_p2 = float(request.form.get('eng_p2'))
        eng_p3 = float(request.form.get('eng_p3'))
        eng_participation = float(request.form.get('eng_participation'))
        eng_midterm = float(request.form.get('eng_midterm'))
        english_point = calculate_english_from_components(
            eng_assessment, eng_writing, eng_p1, eng_p2, eng_p3, eng_participation, eng_midterm
        )

        # İKT komponentləri
        ict_quiz = float(request.form.get('ict_quiz'))
        ict_lab = float(request.form.get('ict_lab'))
        ict_presentation = float(request.form.get('ict_presentation'))
        ict_exam = float(request.form.get('ict_exam'))
        ict_point = calculate_ict_from_components(ict_quiz, ict_lab, ict_presentation, ict_exam)

        # İxtisas_id-yə görə 3-cü fənnin komponentləri
        adiak_point = 0
        history_point = 0

        if ixtisas_id in qrup_1_RI:
            adiak_presentation = float(request.form.get('adiak_presentation'))
            adiak_participation = float(request.form.get('adiak_participation'))
            adiak_midterm = float(request.form.get('adiak_midterm'))
            adiak_final = float(request.form.get('adiak_final'))
            adiak_point = calculate_adiak_from_components(
                adiak_presentation, adiak_participation, adiak_midterm, adiak_final
            )
        elif ixtisas_id in qrup_1_RK or ixtisas_id in qrup_2:
            history_seminar = float(request.form.get('history_seminar'))
            history_interactive = float(request.form.get('history_interactive'))
            history_presentation = float(request.form.get('history_presentation'))
            history_midterm = float(request.form.get('history_midterm'))
            history_final = float(request.form.get('history_final'))
            history_point = calculate_history_from_components(
                history_seminar,
                history_interactive,
                history_presentation,
                history_midterm,
                history_final,
            )
        
        # Tələbə məlumatlarını yenilə
        student.ixtisas_id = ixtisas_id
        student.name = name
        student.surname = surname
        student.english_point = english_point
        student.adiak_point = adiak_point
        student.history_point = history_point
        student.ict_point = ict_point
        
        # Ortalama və qiymətləri yenidən hesabla
        student.average_score = student.calculate_average()
        student._calculate_grades_and_status()
        
        # Təqaüd məlumatlarını sıfırla (yenidən hesablanmalıdır)
        student.scholarship_type = None
        student.rank = None
        
        db.session.commit()
        
        return redirect(url_for('view_students'))
    except Exception as e:
        return f"Xəta: {str(e)}", 400


def identify_csv_columns(headers):
    """CSV sütunlarını avtomatik olaraq identifikasiya edir"""
    column_map = {}
    
    # Normalize headers (lowercase, strip whitespace)
    normalized_headers = {i: h.strip().lower() for i, h in enumerate(headers)}
    
    # Column name patterns for identification
    patterns = {
        'ixtisas_id': ['ixtisas', 'ixtisas_id', 'ixtisasid', 'specialty', 'specialty_id', 'specialtyid', 'id'],
        'name': ['name', 'ad', 'firstname', 'first_name', 'first name'],
        'surname': ['surname', 'soyad', 'lastname', 'last_name', 'last name', 'family name'],
        'eng_assessment': ['eng_assessment', 'english assessment', 'assessment', 'eng assessment', 'english_assessment'],
        'eng_writing': ['eng_writing', 'english writing', 'writing', 'eng writing', 'english_writing', 'graded writing'],
        'eng_p1': ['eng_p1', 'english p1', 'p1', 'presentation 1', 'presentation1', 'eng presentation 1'],
        'eng_p2': ['eng_p2', 'english p2', 'p2', 'presentation 2', 'presentation2', 'eng presentation 2'],
        'eng_p3': ['eng_p3', 'english p3', 'p3', 'presentation 3', 'presentation3', 'eng presentation 3'],
        'eng_participation': ['eng_participation', 'english participation', 'participation', 'eng participation'],
        'eng_midterm': ['eng_midterm', 'english midterm', 'midterm', 'eng midterm', 'english_midterm'],
        'ict_quiz': ['ict_quiz', 'ict quiz', 'quiz', 'ikt quiz'],
        'ict_lab': ['ict_lab', 'ict lab', 'lab', 'laboratory', 'laboratoriya', 'ikt lab'],
        'ict_presentation': ['ict_presentation', 'ict presentation', 'ict prez', 'ikt presentation', 'ikt prez'],
        'ict_exam': ['ict_exam', 'ict exam', 'ict imtahan', 'ikt exam', 'ikt imtahan'],
        'adiak_presentation': ['adiak_presentation', 'adiak presentation', 'adiak prez'],
        'adiak_participation': ['adiak_participation', 'adiak participation', 'adiak aktivlik'],
        'adiak_midterm': ['adiak_midterm', 'adiak midterm'],
        'adiak_final': ['adiak_final', 'adiak final'],
        'history_seminar': ['history_seminar', 'history seminar', 'tarix seminar', 'seminar'],
        'history_interactive': ['history_interactive', 'history interactive', 'tarix interactive', 'interactive'],
        'history_presentation': ['history_presentation', 'history presentation', 'tarix presentation', 'tarix prez'],
        'history_midterm': ['history_midterm', 'history midterm', 'tarix midterm'],
        'history_final': ['history_final', 'history final', 'tarix final'],
    }
    
    for field, possible_names in patterns.items():
        for idx, header in normalized_headers.items():
            if any(pattern in header for pattern in possible_names):
                column_map[field] = idx
                break
    
    return column_map


@app.route('/upload_csv', methods=['POST'])
@admin_required
def upload_csv():
    """CSV faylı yükləyir və tələbələri əlavə edir"""
    if 'csv_file' not in request.files:
        flash('CSV faylı seçilməyib', 'error')
        return redirect(url_for('index'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('Fayl seçilməyib', 'error')
        return redirect(url_for('index'))
    
    if not file.filename.endswith('.csv'):
        flash('Yalnız CSV faylları qəbul olunur', 'error')
        return redirect(url_for('index'))
    
    try:
        # Read CSV file
        stream = io.TextIOWrapper(file.stream, encoding='utf-8-sig')
        csv_reader = csv.reader(stream)
        
        # Get headers
        headers = next(csv_reader)
        column_map = identify_csv_columns(headers)
        
        # Check required columns
        required_fields = ['ixtisas_id', 'name', 'surname']
        missing_fields = [f for f in required_fields if f not in column_map]
        
        if missing_fields:
            flash(f'CSV-də lazımi sütunlar tapılmadı: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('index'))
        
        # Process rows
        added_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because header is row 1
            if not any(row):  # Skip empty rows
                continue
            
            try:
                # Extract basic info
                ixtisas_id = int(row[column_map['ixtisas_id']])
                name = row[column_map['name']].strip()
                surname = row[column_map['surname']].strip()
                
                if not name or not surname:
                    error_count += 1
                    errors.append(f'Sətir {row_num}: Ad və ya soyad boşdur')
                    continue
                
                # Helper function to safely extract float values
                def get_float_value(field_name, default=0):
                    if field_name not in column_map:
                        return default
                    col_idx = column_map[field_name]
                    if col_idx >= len(row):
                        return default
                    value = row[col_idx].strip() if row[col_idx] else ''
                    try:
                        return float(value) if value else default
                    except (ValueError, TypeError):
                        return default
                
                # Extract English components
                eng_assessment = get_float_value('eng_assessment')
                eng_writing = get_float_value('eng_writing')
                eng_p1 = get_float_value('eng_p1')
                eng_p2 = get_float_value('eng_p2')
                eng_p3 = get_float_value('eng_p3')
                eng_participation = get_float_value('eng_participation')
                eng_midterm = get_float_value('eng_midterm')
                
                english_point = calculate_english_from_components(
                    eng_assessment, eng_writing, eng_p1, eng_p2, eng_p3, eng_participation, eng_midterm
                )
                
                # Extract ICT components
                ict_quiz = get_float_value('ict_quiz')
                ict_lab = get_float_value('ict_lab')
                ict_presentation = get_float_value('ict_presentation')
                ict_exam = get_float_value('ict_exam')
                
                ict_point = calculate_ict_from_components(ict_quiz, ict_lab, ict_presentation, ict_exam)
                
                # Extract ADIAK or History components based on ixtisas_id
                adiak_point = 0
                history_point = 0
                
                if ixtisas_id in qrup_1_RI:
                    adiak_presentation = get_float_value('adiak_presentation')
                    adiak_participation = get_float_value('adiak_participation')
                    adiak_midterm = get_float_value('adiak_midterm')
                    adiak_final = get_float_value('adiak_final')
                    adiak_point = calculate_adiak_from_components(
                        adiak_presentation, adiak_participation, adiak_midterm, adiak_final
                    )
                elif ixtisas_id in qrup_1_RK or ixtisas_id in qrup_2:
                    history_seminar = get_float_value('history_seminar')
                    history_interactive = get_float_value('history_interactive')
                    history_presentation = get_float_value('history_presentation')
                    history_midterm = get_float_value('history_midterm')
                    history_final = get_float_value('history_final')
                    history_point = calculate_history_from_components(
                        history_seminar, history_interactive, history_presentation, history_midterm, history_final
                    )
                
                # Create student
                student = Student(ixtisas_id, name, surname, english_point, adiak_point, ict_point, history_point)
                db.session.add(student)
                added_count += 1
                
            except (ValueError, IndexError, KeyError) as e:
                error_count += 1
                errors.append(f'Sətir {row_num}: {str(e)}')
                continue
        
        db.session.commit()
        
        if added_count > 0:
            flash(f'{added_count} tələbə uğurla əlavə edildi', 'success')
        if error_count > 0:
            flash(f'{error_count} sətirdə xəta baş verdi. İlk 5 xəta: {"; ".join(errors[:5])}', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'CSV faylını oxumaq mümkün olmadı: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/preview_csv', methods=['POST'])
@admin_required
def preview_csv():
    """CSV faylının sütunlarını identifikasiya edir və preview göstərir"""
    if 'csv_file' not in request.files:
        return jsonify({'error': 'Fayl seçilməyib'}), 400
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'error': 'Fayl seçilməyib'}), 400
    
    try:
        stream = io.TextIOWrapper(file.stream, encoding='utf-8-sig')
        csv_reader = csv.reader(stream)
        headers = next(csv_reader)
        column_map = identify_csv_columns(headers)
        
        # Get first few rows for preview
        preview_rows = []
        for i, row in enumerate(csv_reader):
            if i >= 3:  # Show only first 3 rows
                break
            if any(row):
                preview_rows.append(row)
        
        return jsonify({
            'headers': headers,
            'column_map': column_map,
            'preview': preview_rows,
            'mapped_fields': list(column_map.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
