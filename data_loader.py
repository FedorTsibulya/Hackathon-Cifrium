import pandas as pd
DATA_PATH = "Датасет (08.04)" # Здесь надо написать путь до папки, откуда будут загружаться csv таблицы для построения отчета

def load_table(filename):
    """
    Загружает любой CSV файл из папки data.
    """
    path = f"{DATA_PATH}/{filename}.csv"
    return pd.read_csv(path)

list_of_table = ['user_lessons', 'user_watched_depth', 'wk_users_courses_actions', 'user_schoolclass_histories', 'students_of_interest',
                 'videos_watched_stats', 'lessons', 'award_badges', 'user_trainings', 'courses_stats', 'user_award_badges', 'trainings',
                 'user_courses', 'user_answers', 'media_view_sessions', 'user_activity_histories'] # перечисление всех таблиц, которые будут использоваться для посроения отчета

dataframes = {}
for table in list_of_table:
  dataframes[table] = load_table(table)