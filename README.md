# BHOS Təqaüd Proqramı

A user-friendly web application designed for BHOS students to determine their scholarships.

## Features

- Add students with their scores for 3 subjects (based on their ixtisas_id)
- Automatically calculate average scores
- Rank students within each ixtisas_id
- Assign scholarships based on quotas:
  - **Əlaçı təqaüdü** (Excellent Scholarship) - Top 30% of free students
  - **Zərbəçi** (Strike Scholarship) - Next 40% of free students
  - **Adi təqaüd** (Regular Scholarship) - Remaining 30% of free students
- View all students and scholarship results

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Add Students**: Go to the main page and fill in the form with student information
   - Select the ixtisas_id (the form will automatically show the correct third subject)
   - Enter student name and surname
   - Enter scores for English, ICT, and either ADIAK or History (depending on ixtisas_id)

2. **View All Students**: Click "Bütün Tələbələr" to see all added students

3. **Calculate Scholarships**: Click "Təqaüd Nəticələri" to:
   - See students ranked by average score within each ixtisas_id
   - View which students received scholarships and what type
   - See a summary of only scholarship recipients

## İxtisas Plans

- 250104 (IT) - 20 free, 10 payable
- 250108 (CE) - 20 free, 30 payable
- 250107 (CS) - 20 free, 30 payable
- 250103 (PAM) - 30 free, 20 payable
- 250110 (DA) - 20 free, 10 payable
- 250102 (CE) - 50 free, 50 payable
- 250101 (PE) - 30 free, 30 payable
- 250109 (Finance) - 20 free, 30 payable
- 250111 (BM) - 20 free, 30 payable

## Subject Groups

- **Group 1 RI** (250104, 250108, 250107, 250103, 250110): English, ADIAK, ICT
- **Group 1 RK** (250101, 250102): English, History, ICT
- **Group 2** (250109, 250111): English, History, ICT
