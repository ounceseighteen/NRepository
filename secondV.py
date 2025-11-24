import sqlite3

def view_students_list():
    """Показать список всех учеников"""
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, first_name, last_name, class FROM students ORDER BY class, last_name')
    students = cursor.fetchall()
    
    print("\n--- Список учеников ---")
    for student in students:
        print(f"{student[0]}. {student[1]} {student[2]} ({student[3]})")
    
    conn.close()
    return students

def view_student_grades():
    """Просмотр оценок выбранного ученика"""
    students = view_students_list()
    
    if not students:
        print("В базе данных нет учеников.")
        return
    
    student_id = input("\nВыберите ID ученика для просмотра оценок: ")
    
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    # Получаем информацию об ученике
    cursor.execute('SELECT first_name, last_name, class FROM students WHERE id = ?', (student_id,))
    student_info = cursor.fetchone()
    
    if not student_info:
        print("Ученик с таким ID не найден!")
        conn.close()
        return
    
    print(f"\n--- Оценки ученика: {student_info[0]} {student_info[1]} ({student_info[2]}) ---")
    
    # Получаем оценки ученика
    cursor.execute('''
        SELECT sub.name, g.grade, g.date, g.quarter
        FROM grades g
        JOIN subjects sub ON g.subject_id = sub.id
        WHERE g.student_id = ?
        ORDER BY g.quarter, sub.name, g.date
    ''', (student_id,))
    
    grades = cursor.fetchall()
    
    if not grades:
        print("У этого ученика пока нет оценок.")
        conn.close()
        return
    
    # Группируем по четвертям
    quarters = {}
    for subject, grade, date, quarter in grades:
        if quarter not in quarters:
            quarters[quarter] = []
        quarters[quarter].append((subject, grade, date))
    
    # Выводим оценки по четвертям
    for quarter in sorted(quarters.keys()):
        print(f"\n{quarter} четверть:")
        for subject, grade, date in quarters[quarter]:
            print(f"  {subject}: {grade} ({date})")
    
    # Средний балл по каждому предмету
    print(f"\n--- Средние баллы ---")
    cursor.execute('''
        SELECT sub.name, AVG(g.grade), COUNT(g.grade)
        FROM grades g
        JOIN subjects sub ON g.subject_id = sub.id
        WHERE g.student_id = ?
        GROUP BY sub.name
        ORDER BY sub.name
    ''', (student_id,))
    
    averages = cursor.fetchall()
    
    for subject, avg_grade, count in averages:
        print(f"  {subject}: {avg_grade:.2f} (всего оценок: {count})")
    
    conn.close()

def view_class_grades():
    """Просмотр оценок всего класса"""
    conn = sqlite3.connect('school_diary.db')
    cursor = conn.cursor()
    
    # Получаем список классов
    cursor.execute('SELECT DISTINCT class FROM students ORDER BY class')
    classes = cursor.fetchall()
    
    if not classes:
        print("В базе данных нет классов.")
        conn.close()
        return
    
    print("\n--- Список классов ---")
    for i, class_info in enumerate(classes, 1):
        print(f"{i}. {class_info[0]}")
    
    class_choice = input("\nВыберите класс: ")
    
    try:
        class_name = classes[int(class_choice) - 1][0]
    except (ValueError, IndexError):
        print("Неверный выбор!")
        conn.close()
        return
    
    print(f"\n--- Оценки класса {class_name} ---")
    
    # Получаем оценки класса
    cursor.execute('''
        SELECT s.first_name, s.last_name, sub.name, g.grade, g.date, g.quarter
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN subjects sub ON g.subject_id = sub.id
        WHERE s.class = ?
        ORDER BY s.last_name, sub.name, g.date
    ''', (class_name,))
    
    grades = cursor.fetchall()
    
    if not grades:
        print("В этом классе пока нет оценок.")
        conn.close()
        return
    
    current_student = None
    for first_name, last_name, subject, grade, date, quarter in grades:
        student_info = f"{first_name} {last_name}"
        if student_info != current_student:
            print(f"\n{student_info}:")
            current_student = student_info
        
        print(f"  {subject}: {grade} ({date}, {quarter} четверть)")
    
    conn.close()

def main_student():
    """Главная функция для ученика"""
    print("Загрузка базы данных...")
    
    while True:
        print("\n" + "="*50)
        print("      ЭЛЕКТРОННЫЙ ДНЕВНИК - РЕЖИМ ПРОСМОТРА")
        print("="*50)
        print("1. Просмотреть оценки ученика")
        print("2. Просмотреть оценки класса")
        print("3. Список всех учеников")
        print("4. Выход")
        
        choice = input("\nВыберите действие: ")
        
        if choice == '1':
            view_student_grades()
        elif choice == '2':
            view_class_grades()
        elif choice == '3':
            view_students_list()
        elif choice == '4':
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main_student()