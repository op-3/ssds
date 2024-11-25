import pandas as pd
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.students_file = os.path.join(self.data_dir, "students.csv")
        self.grades_file = os.path.join(self.data_dir, "grades.csv")
        self.classes_file = os.path.join(self.data_dir, "classes.csv")
        self._initialize_data_files()

    def _initialize_data_files(self):
        """إنشاء ملفات البيانات إذا لم تكن موجودة"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # إنشاء ملف الطلاب
        if not os.path.exists(self.students_file):
            pd.DataFrame({
                'student_id': [],
                'name': [],
                'academic_level': []
            }).to_csv(self.students_file, index=False)

        # إنشاء ملف الدرجات
        if not os.path.exists(self.grades_file):
            pd.DataFrame({
                'student_id': [],
                'course_id': [],
                'semester': [],
                'grade': []
            }).to_csv(self.grades_file, index=False)

        # إنشاء ملف الفصول
        if not os.path.exists(self.classes_file):
            pd.DataFrame({
                'class_id': [],
                'course_id': [],
                'capacity': [],
                'time_slot': []
            }).to_csv(self.classes_file, index=False)

    def add_student(self, student_id, name, academic_level):
        """إضافة طالب جديد"""
        students_df = pd.read_csv(self.students_file)
        new_student = pd.DataFrame({
            'student_id': [student_id],
            'name': [name],
            'academic_level': [academic_level]
        })
        students_df = pd.concat([students_df, new_student], ignore_index=True)
        students_df.to_csv(self.students_file, index=False)

    def add_grade(self, student_id, course_id, semester, grade):
        """إضافة درجة جديدة"""
        grades_df = pd.read_csv(self.grades_file)
        new_grade = pd.DataFrame({
            'student_id': [student_id],
            'course_id': [course_id],
            'semester': [semester],
            'grade': [grade]
        })
        grades_df = pd.concat([grades_df, new_grade], ignore_index=True)
        grades_df.to_csv(self.grades_file, index=False)

    def add_class(self, class_id, course_id, capacity, time_slot):
        """إضافة فصل جديد"""
        classes_df = pd.read_csv(self.classes_file)
        new_class = pd.DataFrame({
            'class_id': [class_id],
            'course_id': [course_id],
            'capacity': [capacity],
            'time_slot': [time_slot]
        })
        classes_df = pd.concat([classes_df, new_class], ignore_index=True)
        classes_df.to_csv(self.classes_file, index=False)

    def get_student_grades(self, student_id):
        """الحصول على درجات طالب معين"""
        grades_df = pd.read_csv(self.grades_file)
        return grades_df[grades_df['student_id'] == student_id]

    def get_all_students(self):
        """الحصول على جميع الطلاب"""
        return pd.read_csv(self.students_file)

    def get_all_classes(self):
        """الحصول على جميع الفصول"""
        return pd.read_csv(self.classes_file)