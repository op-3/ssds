import pandas as pd
import numpy as np

class StudentDistributor:
    def __init__(self):
        self.distribution = {}
        self.class_metrics = {}

    def calculate_class_score(self, class_students):
        """حساب متوسط درجات الفصل"""
        if not class_students:
            return 0
        grades = [student['predicted_grade'] for student in class_students]
        return np.mean(grades)

    def find_best_class(self, student, classes_df):
        """العثور على أفضل فصل للطالب بناءً على التوازن"""
        min_difference = float('inf')
        best_class = None
        student_grade = student['predicted_grade']

        for class_id, students in self.distribution.items():
            # التحقق من سعة الفصل
            class_capacity = classes_df[classes_df['class_id'] == class_id]['capacity'].iloc[0]
            if len(students) >= class_capacity:
                continue

            # حساب متوسط الفصل الحالي
            current_avg = self.calculate_class_score(students)
            
            # حساب متوسط الفصل المحتمل بعد إضافة الطالب
            potential_students = students + [student]
            potential_avg = self.calculate_class_score(potential_students)
            
            # حساب الفرق بين متوسطات الفصول
            max_avg = max([self.calculate_class_score(c) for c in self.distribution.values()])
            min_avg = min([self.calculate_class_score(c) for c in self.distribution.values()])
            current_spread = max_avg - min_avg
            
            # حساب الفرق المحتمل بعد إضافة الطالب
            potential_spread = abs(potential_avg - current_avg)
            
            if potential_spread < min_difference:
                min_difference = potential_spread
                best_class = class_id

        return best_class

    def distribute(self, students, classes, predicted_grades):
        """توزيع الطلاب على الفصول بشكل متوازن"""
        # تحويل البيانات إلى DataFrame للمعالجة السهلة
        students_df = pd.DataFrame(students)
        classes_df = pd.DataFrame(classes)
        
        # إضافة الدرجات المتوقعة للطلاب
        students_df['predicted_grade'] = students_df['student_id'].map(predicted_grades)
        
        # تهيئة قاموس التوزيع
        self.distribution = {class_id: [] for class_id in classes_df['class_id']}
        
        # ترتيب الطلاب عشوائياً ضمن مجموعات المستوى
        students_df['level_group'] = pd.qcut(students_df['predicted_grade'], 
                                           q=min(5, len(students_df)), 
                                           labels=['E', 'D', 'C', 'B', 'A'][:min(5, len(students_df))])
        
        # خلط الطلاب داخل كل مجموعة
        students_df = students_df.sample(frac=1, random_state=42)
        
        # توزيع الطلاب
        for _, student in students_df.iterrows():
            student_dict = {
                'student_id': student['student_id'],
                'name': student['name'],
                'predicted_grade': student['predicted_grade']
            }
            
            # العثور على أفضل فصل للطالب
            best_class = self.find_best_class(student_dict, classes_df)
            
            if best_class is None:
                # إذا لم يتم العثور على فصل مناسب، ابحث عن أي فصل متاح
                for class_id in self.distribution:
                    if len(self.distribution[class_id]) < classes_df[classes_df['class_id'] == class_id]['capacity'].iloc[0]:
                        best_class = class_id
                        break
            
            if best_class is not None:
                self.distribution[best_class].append(student_dict)
            else:
                print(f"تحذير: لم يتم تعيين الطالب {student['name']} لأي فصل")

      
        self.update_class_metrics()
        
        return self.distribution

    def update_class_metrics(self):
        """تحديث مقاييس الفصول"""
        for class_id, students in self.distribution.items():
            if students:
                grades = [s['predicted_grade'] for s in students]
                self.class_metrics[class_id] = {
                    'average': np.mean(grades),
                    'std_dev': np.std(grades),
                    'min': min(grades),
                    'max': max(grades),
                    'count': len(students)
                }
            else:
                self.class_metrics[class_id] = {
                    'average': 0,
                    'std_dev': 0,
                    'min': 0,
                    'max': 0,
                    'count': 0
                }

    def get_distribution_metrics(self):
        """الحصول على مقاييس التوزيع"""
        return self.class_metrics

    def get_overall_metrics(self):
        """الحصول على المقاييس الإجمالية للتوزيع"""
        all_grades = []
        class_averages = []
        
        for students in self.distribution.values():
            if students:
                grades = [s['predicted_grade'] for s in students]
                all_grades.extend(grades)
                class_averages.append(np.mean(grades))
        
        if all_grades:
            return {
                'overall_average': np.mean(all_grades),
                'overall_std_dev': np.std(all_grades),
                'class_avg_difference': max(class_averages) - min(class_averages) if class_averages else 0,
                'total_students': len(all_grades)
            }
        return {
            'overall_average': 0,
            'overall_std_dev': 0,
            'class_avg_difference': 0,
            'total_students': 0
        }

    def export_distribution(self, filename):
        """تصدير التوزيع إلى ملف CSV"""
        rows = []
        for class_id, students in self.distribution.items():
            class_metrics = self.class_metrics[class_id]
            for student in students:
                rows.append({
                    'class_id': class_id,
                    'student_id': student['student_id'],
                    'student_name': student['name'],
                    'predicted_grade': student['predicted_grade'],
                    'class_average': class_metrics['average'],
                    'class_std_dev': class_metrics['std_dev']
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        return df

    def print_distribution_summary(self):
        """طباعة ملخص التوزيع"""
        print("\n=== ملخص التوزيع ===")
        
        overall_metrics = self.get_overall_metrics()
        print(f"\nالمقاييس الإجمالية:")
        print(f"المتوسط الكلي: {overall_metrics['overall_average']:.2f}")
        print(f"الانحراف المعياري الكلي: {overall_metrics['overall_std_dev']:.2f}")
        print(f"الفرق بين متوسطات الفصول: {overall_metrics['class_avg_difference']:.2f}")
        
        print("\nإحصائيات الفصول:")
        for class_id, metrics in self.class_metrics.items():
            print(f"\nالفصل {class_id}:")
            print(f"عدد الطلاب: {metrics['count']}")
            print(f"المتوسط: {metrics['average']:.2f}")
            print(f"الانحراف المعياري: {metrics['std_dev']:.2f}")
            print(f"أقل درجة: {metrics['min']:.2f}")
            print(f"أعلى درجة: {metrics['max']:.2f}")