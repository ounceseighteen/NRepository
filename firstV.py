import sqlite3
from datetime import date
from datetime import datetime

def add_student():
    """Добавление нового ученика"""
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    print("\n--- Добавление ученика ---")
    first_name = input("Имя: ")
    last_name = input("Фамилия: ")
    class_name = input("Класс (например, 10А): ")
    
    cursor.execute('''
        INSERT INTO students (first_name, last_name, class)
        VALUES (?, ?, ?)
    ''', (first_name, last_name, class_name))
    
    conn.commit()
    conn.close()
    print("Ученик успешно добавлен!")

def add_grade():
    """Добавление оценки"""
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    print("\n--- Добавление оценки ---")
    
    # Показываем учеников
    cursor.execute('SELECT id, first_name, last_name, class FROM students ORDER BY class, last_name')
    students = cursor.fetchall()
    
    if not students:
        print("В базе данных нет учеников!")
        conn.close()
        return
    
    print("\nСписок учеников:")
    for student in students:
        print(f"{student[0]}. {student[1]} {student[2]} ({student[3]})")
    
    student_id = input("\nВыберите ID ученика: ")
    
    # Показываем предметы
    cursor.execute('SELECT id, name FROM subjects ORDER BY name')
    subjects = cursor.fetchall()
    
    print("\nСписок предметов:")
    for subject in subjects:
        print(f"{subject[0]}. {subject[1]}")
    
    subject_id = input("\nВыберите ID предмета: ")
    grade = input("Оценка (1-5): ")
    quarter = input("Четверть (1-4): ")
    
    # Получаем дату в формате ДД.ММ.ГГГГ
    today = date.today().strftime('%d.%m.%Y')
    
    cursor.execute('''
        INSERT INTO grades (student_id, subject_id, grade, date, quarter)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_id, subject_id, grade, today, quarter))
    
    conn.commit()
    conn.close()
    print("Оценка успешно добавлена!")

def view_all_grades():
    """Просмотр всех оценок (всех учеников)"""
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    print("\n--- Все оценки ---")
    
    cursor.execute('''
        SELECT s.first_name, s.last_name, s.class, sub.name, g.grade, g.date, g.quarter
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN subjects sub ON g.subject_id = sub.id
        ORDER BY s.class, s.last_name, sub.name, g.date
    ''')
    
    grades = cursor.fetchall()
    
    if not grades:
        print("Оценок пока нет.")
        conn.close()
        return
    
    current_student = None
    for grade in grades:
        student_info = f"{grade[0]} {grade[1]} ({grade[2]})"
        if student_info != current_student:
            print(f"\n{student_info}:")
            current_student = student_info
        
        print(f"  {grade[3]}: {grade[4]} ({grade[5]}, {grade[6]} четверть)")
    
    conn.close()

def count_twos_in_quarter():
    """Эксперимент: Подсчет двоек в четверти"""
    print("\n=== ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ: Подсчет двоек в четверти ===")
    
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    quarter = input("Введите номер четверти (1-4): ")
    
    # Подсчет всех двоек в указанной четверти
    cursor.execute('''
        SELECT s.class, COUNT(*) as twos_count
        FROM grades g
        JOIN students s ON g.student_id = s.id
        WHERE g.grade = 2 AND g.quarter = ?
        GROUP BY s.class
        ORDER BY s.class
    ''', (quarter,))
    
    results = cursor.fetchall()
    
    print(f"\nКоличество двоек в {quarter} четверти по классам:")
    total_twos = 0
    for class_name, count in results:
        print(f"Класс {class_name}: {count} двоек")
        total_twos += count
    
    print(f"\nВсего двоек в {quarter} четверти: {total_twos}")
    
    conn.close()

def calculate_average_grades():
    """Эксперимент: Расчет средних оценок по классам"""
    print("\n=== ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ: Средние оценки по классам ===")
    
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    quarter = input("Введите номер четверти (1-4 или Enter для всех): ")
    
    if quarter:
        # Средние оценки по классам для конкретной четверти
        cursor.execute('''
            SELECT s.class, sub.name, AVG(g.grade), COUNT(g.grade)
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN subjects sub ON g.subject_id = sub.id
            WHERE g.quarter = ?
            GROUP BY s.class, sub.name
            ORDER BY s.class, sub.name
        ''', (quarter,))
    else:
        # Средние оценки по классам за все время
        cursor.execute('''
            SELECT s.class, sub.name, AVG(g.grade), COUNT(g.grade)
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN subjects sub ON g.subject_id = sub.id
            GROUP BY s.class, sub.name
            ORDER BY s.class, sub.name
        ''')
    
    results = cursor.fetchall()
    
    current_class = None
    print(f"\nСредние оценки {'в ' + quarter + ' четверти' if quarter else 'за все время'}:")
    
    for class_name, subject, avg_grade, count in results:
        if class_name != current_class:
            print(f"\nКласс {class_name}:")
            current_class = class_name
        
        print(f"  {subject}: {avg_grade:.2f} (всего оценок: {count})")
    
    conn.close()

def main_teacher():
    """Главная функция для преподавателя"""
    print("Загрузка базы данных...")
    
    while True:
        print("\n" + "="*50)
        print("      ЭЛЕКТРОННЫЙ ДНЕВНИК - РЕЖИМ ПРЕПОДАВАТЕЛЯ")
        print("="*50)
        print("1. Добавить ученика")
        print("2. Добавить оценку")
        print("3. Просмотреть все оценки")
        print("4. Подсчет двоек в четверти")
        print("5. Средние оценки по классам")
        print("6. Выход")
        
        choice = input("\nВыберите действие: ")
        
        if choice == '1':
            add_student()
        elif choice == '2':
            add_grade()
        elif choice == '3':
            view_all_grades()
        elif choice == '4':
            count_twos_in_quarter()
        elif choice == '5':
            calculate_average_grades()
        elif choice == '6':
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main_teacher()