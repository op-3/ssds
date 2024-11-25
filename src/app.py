import streamlit as st
import pandas as pd
from database import Database
from predictor import GradePredictor
from distributor import StudentDistributor
import os

class App:
    def __init__(self):
        self.db = Database()
        self.predictor = GradePredictor()
        self.distributor = StudentDistributor()

    def run(self):
        st.title("نظام توزيع الطلاب الذكي")
        
        menu = ["إدارة البيانات", "التنبؤ", "التوزيع", "عرض النتائج"]
        choice = st.sidebar.selectbox("القائمة", menu)
        
        if choice == "إدارة البيانات":
            self.show_data_management()
        elif choice == "التنبؤ":
            self.show_prediction_page()
        elif choice == "التوزيع":
            self.show_distribution_page()
        else:
            self.show_results_page()

    def show_data_management(self):
        st.header("إدارة البيانات")
        
        tab1, tab2, tab3 = st.tabs(["الطلاب", "الدرجات", "الفصول"])
        
        with tab1:
            st.subheader("إضافة طالب جديد")
            student_id = st.text_input("رقم الطالب")
            student_name = st.text_input("اسم الطالب")
            academic_level = st.selectbox("المستوى الدراسي", [1, 2, 3, 4])
            
            if st.button("إضافة طالب"):
                self.db.add_student(student_id, student_name, academic_level)
                st.success("تم إضافة الطالب بنجاح")
        
        with tab2:
            st.subheader("إضافة درجة")
            students = self.db.get_all_students()
            selected_student = st.selectbox(
                "اختر الطالب",
                options=students['student_id'].tolist(),
                format_func=lambda x: f"{x} - {students[students['student_id']==x]['name'].iloc[0]}"
            )
            course_id = st.text_input("رمز المادة")
            semester = st.text_input("الفصل الدراسي")
            grade = st.number_input("الدرجة", 0, 100)
            
            if st.button("إضافة درجة"):
                self.db.add_grade(selected_student, course_id, semester, grade)
                st.success("تم إضافة الدرجة بنجاح")
        
        with tab3:
            st.subheader("إضافة فصل دراسي")
            class_id = st.text_input("رمز الفصل")
            course_id = st.text_input("رمز المادة", key="class_course_id")
            capacity = st.number_input("السعة", 1, 100)
            time_slot = st.text_input("وقت المحاضرة")
            
            if st.button("إضافة فصل"):
                self.db.add_class(class_id, course_id, capacity, time_slot)
                st.success("تم إضافة الفصل بنجاح")

    def show_prediction_page(self):
        st.header("التنبؤ بالدرجات")
        
        if st.button("تدريب النموذج"):
            try:
                grades = pd.read_csv(self.db.grades_file)
                score = self.predictor.train(grades)
                st.success(f"تم تدريب النموذج بنجاح. دقة النموذج: {score:.2f}")
            except Exception as e:
                st.error(f"حدث خطأ أثناء التدريب: {str(e)}")

    def show_distribution_page(self):
        st.header("توزيع الطلاب")
        
        if st.button("توزيع الطلاب"):
            try:
                # تحميل البيانات
                students = self.db.get_all_students()
                classes = self.db.get_all_classes()
                grades = pd.read_csv(self.db.grades_file)
                
                # التنبؤ بالدرجات لكل طالب
                predicted_grades = {}
                for _, student in students.iterrows():
                    student_grades = grades[grades['student_id'] == student['student_id']]['grade'].tolist()
                    if len(student_grades) >= 3:
                        predicted_grades[student['student_id']] = self.predictor.predict(student_grades)
                    else:
                        predicted_grades[student['student_id']] = np.mean(student_grades) if student_grades else 50
                
                # توزيع الطلاب
                distribution = self.distributor.distribute(
                    students.to_dict('records'),
                    classes.to_dict('records'),
                    predicted_grades
                )
                
                # عرض النتائج
                for class_id, students in distribution.items():
                    st.subheader(f"الفصل {class_id}")
                    st.write(pd.DataFrame(students))
                
                # تصدير النتائج
                self.distributor.export_distribution("data/distribution_results.csv")
                st.success("تم التوزيع وحفظ النتائج بنجاح")
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء التوزيع: {str(e)}")

    def show_results_page(self):
        st.header("نتائج التوزيع")
        
        if os.path.exists("data/distribution_results.csv"):
            results = pd.read_csv("data/distribution_results.csv")
            st.write(results)
            
            # تحليلات إضافية
            st.subheader("إحصائيات التوزيع")
            st.write("متوسط الدرجات المتوقعة لكل فصل:")
            avg_grades = results.groupby('class_id')['predicted_grade'].mean()
            st.bar_chart(avg_grades)
        else:
            st.info("لم يتم العثور على نتائج التوزيع. قم بتنفيذ عملية التوزيع أولاً.")

if __name__ == "__main__":
    app = App()
    app.run()