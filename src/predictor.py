import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib
import os

class GradePredictor:
    def __init__(self):
        self.model = None
        self.models_dir = "models"
        self.model_path = os.path.join(self.models_dir, "grade_predictor.joblib")
        self._initialize_models_directory()

    def _initialize_models_directory(self):
        """إنشاء مجلد النماذج إذا لم يكن موجوداً"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def prepare_features(self, student_grades):
        """تحضير البيانات للتدريب"""
        # حساب متوسط الدرجات السابقة
        features = []
        targets = []
        
        for student_id in student_grades['student_id'].unique():
            student_data = student_grades[student_grades['student_id'] == student_id]
            sorted_grades = student_data.sort_values('semester')
            
            for i in range(1, len(sorted_grades)):
                prev_grades = sorted_grades.iloc[:i]['grade'].tolist()
                while len(prev_grades) < 3:  # نحتاج 3 درجات سابقة على الأقل
                    prev_grades.append(0)
                features.append(prev_grades[-3:])  # آخر 3 درجات
                targets.append(sorted_grades.iloc[i]['grade'])
        
        return np.array(features), np.array(targets)

    def train(self, student_grades):
        """تدريب النموذج"""
        X, y = self.prepare_features(student_grades)
        
        if len(X) < 2:  # نحتاج بيانات كافية للتدريب
            raise ValueError("لا توجد بيانات كافية للتدريب")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # حفظ النموذج
        joblib.dump(self.model, self.model_path)
        
        # حساب دقة النموذج
        score = self.model.score(X_test, y_test)
        return score

    def predict(self, previous_grades):
        """التنبؤ بالدرجة المتوقعة"""
        if self.model is None:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                raise ValueError("لم يتم تدريب النموذج بعد")

        # تحضير البيانات للتنبؤ
        grades = previous_grades[-3:]  # آخر 3 درجات
        while len(grades) < 3:
            grades.insert(0, 0)
        
        prediction = self.model.predict([grades])[0]
        return max(0, min(100, prediction))  # التأكد من أن الدرجة بين 0 و 100