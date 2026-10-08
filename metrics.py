"""# Расчет метрик"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pytz import timezone, UTC


def _viewer_mask(media_df, user_id):
    """Маска строк media_view_sessions для пользователя.

    viewer_id в выгрузке хранится строкой с разделителями тысяч ("665,767"),
    поэтому прямое сравнение с числовым user_id ничего не находит.
    """
    ids = pd.to_numeric(
        media_df['viewer_id'].astype(str).str.replace(',', '', regex=False),
        errors='coerce'
    )
    return ids == user_id


def calculate_course_completion_percent(user_id, dataframes):
    """
    Метрика 1: Курс пройден на n процентов (количество выполненных заданий / общее количество заданий)
    """
    if 'user_courses' not in list(dataframes.keys()):
        print("Таблица 'user_courses' не найдена")
        return 0.0

    user_courses = dataframes['user_courses']
    user_course = user_courses[user_courses['user_id'] == user_id]

    if user_course.empty:
        return 0.0

    solved_tasks = user_course['wk_solved_task_count'].iloc[0]
    max_tasks = user_course['wk_max_task_count'].iloc[0]

    if max_tasks == 0:
        return 0.0

    return solved_tasks / max_tasks * 100

def calculate_earned_points_ratio(user_id, dataframes):
    """
    Метрика 2: Заработанные баллы / общее количество баллов
    """
    if 'user_courses' not in list(dataframes.keys()):
        print("Таблица 'user_courses' не найдена")
        return 0.0

    user_courses = dataframes['user_courses']
    user_course = user_courses[user_courses['user_id'] == user_id]

    if user_course.empty:
        return 0.0

    earned_points = user_course['wk_points'].iloc[0]
    max_points = user_course['wk_max_points'].iloc[0]

    if max_points == 0:
        return 0.0

    return earned_points / max_points

def calculate_started_tasks_ratio(user_id, dataframes):
    """
    Метрика 3: Количество начатых задач / общее количество задач
    """
    # Нужные таблицы
    if 'user_answers' not in list(dataframes.keys()):
        print("Таблица 'user_answers' не найдена")
        return 0.0
    if 'user_courses' not in list(dataframes.keys()):
        print("Таблица 'user_courses' не найдена")
        return 0.0
    if 'lessons' not in list(dataframes.keys()):
        print("Таблица 'lessons' не найдена")
        return 0.0

    # Джойним user_answers с user_courses, чтобы получить course_id
    user_answers = dataframes['user_answers'][dataframes['user_answers']['user_id'] == user_id].copy()
    user_courses = dataframes['user_courses'][dataframes['user_courses']['user_id'] == user_id]

    if user_answers.empty or user_courses.empty:
        return 0.0

    # Джойним по users_course_id (если есть такая колонка в user_answers)
    if 'users_course_id' in user_answers.columns:
        merged = user_answers.merge(
            user_courses[['id', 'course_id']],
            left_on='users_course_id',
            right_on='id',
            how='inner'
        )
    else:
        return 0.0

    if merged.empty:
        return 0.0

    # Получаем общее количество задач в курсе
    course_id = merged['course_id'].iloc[0]
    lessons_course = dataframes['lessons'][dataframes['lessons']['course_id'] == course_id]
    max_tasks = lessons_course['wk_task_count'].sum()

    if max_tasks == 0:
        return 0.0
    started_tasks = merged['task_id'].nunique()
    return started_tasks / max_tasks

def calculate_solved_tasks_ratio(user_id, dataframes):
    """
    Метрика 4: Количество решенных задач / общее количество задач
    """
    if 'user_answers' not in list(dataframes.keys()):
        print("Таблица 'user_answers' не найдена")
        return 0.0
    if 'user_courses' not in list(dataframes.keys()):
        print("Таблица 'user_courses' не найдена")
        return 0.0
    if 'lessons' not in list(dataframes.keys()):
        print("Таблица 'lessons' не найдена")
        return 0.0

    user_answers = dataframes['user_answers'][
        (dataframes['user_answers']['user_id'] == user_id) &
        (dataframes['user_answers']['solved'] == True)
    ].copy()
    user_courses = dataframes['user_courses'][dataframes['user_courses']['user_id'] == user_id]

    if user_answers.empty or user_courses.empty:
        return 0.0

    if 'users_course_id' in user_answers.columns:
        merged = user_answers.merge(
            user_courses[['id', 'course_id']],
            left_on='users_course_id',
            right_on='id',
            how='inner'
        )
    else:
        return 0.0

    if merged.empty:
        return 0.0

    course_id = merged['course_id'].iloc[0]
    lessons_course = dataframes['lessons'][dataframes['lessons']['course_id'] == course_id]
    max_tasks = lessons_course['wk_task_count'].sum()

    if max_tasks == 0:
        return 0.0

    solved_tasks = merged['task_id'].nunique()
    return solved_tasks / max_tasks

def calculate_solved_to_started_ratio(user_id, dataframes):
    """
    Метрика 5: Количество решенных задач / количество начатых задач
    """
    if 'user_answers' not in list(dataframes.keys()):
        print("Таблица 'user_answers' не найдена")
        return 0.0

    user_answers = dataframes['user_answers'][dataframes['user_answers']['user_id'] == user_id]

    if user_answers.empty:
        return 0.0

    started_tasks = user_answers['task_id'].nunique()
    solved_tasks = user_answers[user_answers['solved'] == True]['task_id'].nunique()

    if started_tasks == 0:
        return 0.0

    return solved_tasks / started_tasks

def calculate_avg_attempts_per_task(user_id, dataframes):
    """
    Метрика 6: Среднее количество попыток на одну задачу
    """
    if 'user_answers' not in list(dataframes.keys()):
        print("Таблица 'user_answers' не найдена")
        return 0.0

    user_answers = dataframes['user_answers'][dataframes['user_answers']['user_id'] == user_id]

    if user_answers.empty:
        return 0.0

    return user_answers['attempts'].mean()

def calculate_max_attempts_per_task(user_id, dataframes):
    """
    Метрика 7: Максимальное количество попыток на одну задачу
    """
    if 'user_answers' not in list(dataframes.keys()):
        print("Таблица 'user_answers' не найдена")
        return 0.0

    user_answers = dataframes['user_answers'][dataframes['user_answers']['user_id'] == user_id]

    if user_answers.empty:
        return 0

    return int(user_answers['attempts'].max())

def calculate_total_points_earned_from_tasks(user_id, dataframes):
    """
    Метрика 8: Сумма баллов за задачи (без видео, тестов, бонусов)
    """
    if 'user_answers' not in list(dataframes.keys()):
        print("Таблица 'user_answers' не найдена")
        return 0.0

    user_answers = dataframes['user_answers'][dataframes['user_answers']['user_id'] == user_id]

    if user_answers.empty:
        return 0.0

    return float(user_answers['points'].sum())

def calculate_videos_started_count(user_id, dataframes):
    """
    Метрика 9: Количество начатых видео
    """
    if 'media_view_sessions' not in list(dataframes.keys()):
        print("Таблица 'media_view_sessions' не найдена")
        return 0.0

    media_df = dataframes['media_view_sessions']
    user_views = media_df[_viewer_mask(media_df, user_id)]

    if user_views.empty:
        return 0

    return int(user_views['resource_id'].nunique())

def calculate_avg_watch_percent(user_id, dataframes):
    """
    Метрика 10: Средний процент досмотра видео
    """
    if 'media_view_sessions' not in list(dataframes.keys()):
        print("Таблица 'media_view_sessions' не найдена")
        return 0.0

    media_df = dataframes['media_view_sessions']
    user_views = media_df[_viewer_mask(media_df, user_id)].copy()

    if user_views.empty:
        return 0.0

    user_views['viewed_segments_count'] = pd.to_numeric(user_views['viewed_segments_count'], errors='coerce')
    user_views['segments_total'] = pd.to_numeric(user_views['segments_total'], errors='coerce')

    user_views = user_views.dropna(subset=['viewed_segments_count', 'segments_total'])

    if user_views.empty:
        return 0.0

    user_views['watch_percent'] = user_views['viewed_segments_count'] / user_views['segments_total']

    return float(user_views['watch_percent'].mean())

def calculate_watched_to_started_videos_ratio(user_id, dataframes):
    """
    Метрика 11: Просмотренные видео / начатые видео
    """
    if 'media_view_sessions' not in list(dataframes.keys()):
        print("Таблица 'media_view_sessions' не найдена")
        return 0.0

    media_df = dataframes['media_view_sessions']
    user_views = media_df[_viewer_mask(media_df, user_id)].copy()

    if user_views.empty:
        return 0.0

    user_views['viewed_segments_count'] = pd.to_numeric(user_views['viewed_segments_count'], errors='coerce')
    user_views['segments_total'] = pd.to_numeric(user_views['segments_total'], errors='coerce')

    user_views = user_views.dropna(subset=['viewed_segments_count', 'segments_total'])

    if user_views.empty:
        return 0.0

    started_videos = len(user_views)
    fully_watched = len(user_views[user_views['viewed_segments_count'] == user_views['segments_total']])

    if started_videos == 0:
        return 0.0

    return fully_watched / started_videos

def calculate_lessons_with_video_viewed_count(user_id, dataframes):
    """
    Метрика 12: Количество уроков, где пользователь смотрел видео
    """
    if 'user_lessons' not in list(dataframes.keys()):
        print("Таблица 'user_lessons' не найдена")
        return 0.0

    user_lessons = dataframes['user_lessons']
    user_lessons_user = user_lessons[user_lessons['user_id'] == user_id]

    if user_lessons_user.empty:
        return 0

    if 'video_visited' not in user_lessons_user.columns:
        return 0

    return int(user_lessons_user[user_lessons_user['video_visited'] == True].shape[0])

def calculate_completed_lessons_count(user_id, dataframes):
    """
    Метрика 13: Количество полностью завершённых уроков
    """
    if 'user_lessons' not in list(dataframes.keys()):
        print("Таблица 'user_lessons' не найдена")
        return 0.0

    user_lessons = dataframes['user_lessons']
    user_lessons_user = user_lessons[user_lessons['user_id'] == user_id]

    if user_lessons_user.empty:
        return 0

    if 'solved' not in user_lessons_user.columns:
        return 0

    return int(user_lessons_user[user_lessons_user['solved'] == True].shape[0])

def calculate_completed_to_opened_lessons_ratio(user_id, dataframes):
    """
    Метрика 14: Завершенные уроки / открытые уроки
    """
    if 'user_lessons' not in list(dataframes.keys()):
        print("Таблица 'user_lessons' не найдена")
        return 0.0

    user_lessons = dataframes['user_lessons']
    user_lessons_user = user_lessons[user_lessons['user_id'] == user_id]

    if user_lessons_user.empty:
        return 0.0

    opened_lessons = user_lessons_user.shape[0]

    if 'solved' not in user_lessons_user.columns:
        return 0.0

    completed_lessons = user_lessons_user[user_lessons_user['solved'] == True].shape[0]

    if opened_lessons == 0:
        return 0.0

    return completed_lessons / opened_lessons

def calculate_max_tasks_in_course(user_id, dataframes):
    """
    Метрика 15: Количество задач в уроках курса
    """
    # Джойним user_courses с lessons, чтобы получить course_id и задачи
    if 'user_lessons' not in list(dataframes.keys()):
        print("Таблица 'user_lessons' не найдена")
        return 0.0
    if 'lessons' not in list(dataframes.keys()):
        print("Таблица 'lessons' не найдена")
        return 0.0

    user_courses = dataframes['user_courses'][dataframes['user_courses']['user_id'] == user_id]

    if user_courses.empty:
        return 0

    course_id = user_courses['course_id'].iloc[0]
    lessons_course = dataframes['lessons'][dataframes['lessons']['course_id'] == course_id]

    if lessons_course.empty:
        return 0

    if 'wk_task_count' not in lessons_course.columns:
        return 0

    return int(lessons_course['wk_task_count'].sum())


def get_better_than_percent_in_city(user_id, dataframes):
    """
    Лучше, чем n% ребят из твоего города (по баллам).
    Возвращает процент учеников в том же городе, у которых балл <= балла user_id.
    """
    if 'courses_stats' not in list(dataframes.keys()):
        print("Таблица 'courses_stats' не найдена")
        return None

    df = dataframes['courses_stats']

    # Находим строку пользователя
    user_row = df[df['user_id'] == user_id]

    if user_row.empty:
        print(f"Пользователь {user_id} не найден в courses_stats")
        return None

    user_city = user_row['Муниципалитет'].iloc[0]
    user_points = user_row['Набрал баллов'].iloc[0]

    # Фильтруем по тому же городу
    same_city_df = df[df['Муниципалитет'] == user_city]

    if len(same_city_df) == 0:
        return 100  # Если он один в городе, он лучше 100% (самого себя)

    count_better_or_equal = (same_city_df['Набрал баллов'] <= user_points).sum()
    total_in_city = len(same_city_df)

    percent = int((count_better_or_equal / total_in_city) * 100)
    return percent

def get_lessons_watched_count(user_id, dataframes):
    """
    Количество посещенных лекций и вебинаров.
    Возвращает целое число из колонки 'Всего просмотров уроков'.
    """
    if 'courses_stats' not in list(dataframes.keys()):
        print("Таблица 'courses_stats' не найдена")
        return 0

    df = dataframes['courses_stats']
    user_row = df[df['user_id'] == user_id]

    if user_row.empty:
        return 0
    return int(user_row['Всего просмотров уроков'].iloc[0])

def get_studied_themes_count(user_id, dataframes):
    """
    Количество изученных тем.
    Считает количество уникальных записей в user_lessons для данного user_id.
    """
    if 'user_lessons' not in list(dataframes.keys()):
        print("Таблица 'user_lessons' не найдена")
        return 0

    df = dataframes['user_lessons']
    user_lessons = df[df['user_id'] == user_id]

    # Возвращаем количество записейв таблице user_lessons
    return len(user_lessons)

def get_trainings_completed_info(user_id, dataframes):
    """
    Ты выполнил n домашних заданий (тренингов) со средним баллом n.
    Возвращает (количество_тренингов, средний_балл).
    """
    if 'user_lessons' not in list(dataframes.keys()) or 'lessons' not in list(dataframes.keys()):
        print("Таблица 'user_lessons' или 'lessons' не найдена")
        return 0, 0.0

    user_lessons_df = dataframes['user_lessons']
    lessons_df = dataframes['lessons']
    # Данные пользователя
    user_data = user_lessons_df[user_lessons_df['user_id'] == user_id]
    if user_data.empty:
        return 0, 0.0
    # Объединение с lessons для получения wk_max_points
    merged = user_data.merge(
        lessons_df[['id', 'wk_max_points']],
        left_on='lesson_id',
        right_on='id',
        how='inner'
    )

    # Считаем процент выполнения для каждого тренинга
    merged['score_ratio'] = merged['wk_points'] / merged['wk_max_points']
    average_score = merged['score_ratio'].mean()

    unique_lessons_count = user_lessons_df[user_lessons_df['user_id'] == user_id]['lesson_id'].nunique()

    return unique_lessons_count, float(average_score)

def get_max_time_spent_on_task(user_id, dataframes):
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return None

    df = dataframes['user_answers'].copy()
    mask = (df['user_id'] == user_id) & (df['solved'] == True)

    # Дату форматируем
    df.loc[mask, 'created_at'] = pd.to_datetime(df.loc[mask, 'created_at'])
    df.loc[mask, 'submitted_at'] = pd.to_datetime(df.loc[mask, 'submitted_at'])
    df.loc[mask, 'time_spent'] = df.loc[mask, 'submitted_at'] - df.loc[mask, 'created_at']

    # Теперь фильтруем
    user_solved = df[mask]

    if user_solved.empty:
        return None

    max_time = user_solved['time_spent'].max()
    return max_time

def get_webinars_total_duration_original_style(user_id, dataframes):
    """
    Суммирует длительность видео (wk_video_duration) для всех видео,
    которые пользователь открывал
    ВАЖНО: Сейчас не работает, так как wk_video_duration заполнен NaN.
    """
    if 'media_view_sessions' not in list(dataframes.keys()) or 'lessons' not in list(dataframes.keys()):
        print("Таблица 'media_view_sessions' или 'lessons' не найдена")
        return None

    media_df = dataframes['media_view_sessions'].copy()
    lessons_df = dataframes['lessons'].copy()

    media_df['viewer_id_str'] = media_df['viewer_id'].astype(str).str.replace(',', '')
    user_id_str = str(user_id)

    # Фильтруем просмотры пользователя
    user_views = media_df[media_df['viewer_id_str'] == user_id_str]

    if user_views.empty:
        return 0

    # Разделяем на вебинары (Group) и записи (Lesson)
    vebs = user_views[user_views['resource_type'] == 'Group']['resource_id'].tolist()
    pre_recorded = user_views[user_views['resource_type'] == 'Lesson']['resource_id'].tolist()

    total_time_vebs = 0
    for resource_id in vebs:
        lesson_row = lessons_df[lessons_df['id'] == resource_id]
        if not lesson_row.empty:
            duration = lesson_row['wk_video_duration'].iloc[0]
            if pd.notna(duration):
                total_time_vebs += duration

    # Суммируем для записей уроков
    total_time_pre_recorded = 0
    for resource_id in pre_recorded:
        lesson_row = lessons_df[lessons_df['id'] == resource_id]
        if not lesson_row.empty:
            duration = lesson_row['wk_video_duration'].iloc[0]
            if pd.notna(duration):
                total_time_pre_recorded += duration

    total_time = total_time_vebs + total_time_pre_recorded
    return total_time

def get_user_awards_count(user_id, dataframes):
    """Подсчёт количества полученных достижений для конкретного пользователя """
    if 'user_award_badges' not in dataframes:
        print("Таблица 'user_award_badges' не найдена")
        return 0
    user_award_badges_df = dataframes['user_award_badges']

    # Фильтруем по конкретному пользователю
    user_awards = user_award_badges_df[user_award_badges_df['user_id'] == user_id]
    awards_count = len(user_awards)
    return awards_count

def get_first_attempt_success_rate(user_id, dataframes):
    """
    Расчёт доли задач, решённых с первой попытки
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return [0, 0, 0]
    user_answers_df = dataframes['user_answers']

    # Фильтруем по пользователю и только решённые задачи
    user_solved = user_answers_df[
        (user_answers_df['user_id'] == user_id) &
        (user_answers_df['solved'] == True) ]

    total_solved = len(user_solved)
    if total_solved == 0:
        return 0, 0, 0

    # Задачи, решённые с первой попытки (attempts == 1)
    first_attempt_solved = len(user_solved[user_solved['attempts'] == 1])

    # Доля в процентах
    rate = round(first_attempt_solved / total_solved * 100, 2)
    return rate

def get_not_first_attempt_success_rate(user_id, dataframes):
    """
    Расчёт доли задач, решённых НЕ с первой попытки
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return [0, 0, 0]

    user_answers_df = dataframes['user_answers']

    # Фильтруем по пользователю и только решённые задачи
    user_solved = user_answers_df[
        (user_answers_df['user_id'] == user_id) &
        (user_answers_df['solved'] == True)
    ]

    total_solved = len(user_solved)

    if total_solved == 0:
        return 0, 0, 0

    # Задачи, решённые не с первой попытки (attempts > 1)
    not_first_attempt_solved = len(user_solved[user_solved['attempts'] > 1])

    # Доля в процентах
    rate = round(not_first_attempt_solved / total_solved * 100, 2)
    return [not_first_attempt_solved, total_solved, rate]

def get_unsolved_tasks_count(user_id, dataframes):
    """
    Подсчёт количества задач, которые пользователь так и не решил
    Возвращает:
    - unsolved_count: количество нерешённых задач
    - total_tasks: общее количество задач, с которыми взаимодействовал пользователь
    - unsolved_rate: доля нерешённых задач (в процентах)
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return [0, 0, 0]

    user_answers_df = dataframes['user_answers']

    # Фильтруем по пользователю
    user_tasks = user_answers_df[user_answers_df['user_id'] == user_id]

    total_tasks = len(user_tasks)

    if total_tasks == 0:
        return 0, 0, 0

    # Нерешённые задачи (solved == False)
    unsolved_tasks = user_tasks[user_tasks['solved'] == False]
    unsolved_count = len(unsolved_tasks)

    # Доля в процентах
    unsolved_rate = round(unsolved_count / total_tasks * 100, 2)
    return [unsolved_count, total_tasks, unsolved_rate]

def get_avg_points_per_attempt(user_id, dataframes):
    """
    Расчёт среднего количества баллов, которое приносит одна попытка
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return 0, 0, 0

    user_answers_df = dataframes['user_answers']

    # Фильтруем по пользователю
    user_tasks = user_answers_df[user_answers_df['user_id'] == user_id]

    if len(user_tasks) == 0:
        return [0, 0, 0]

    # Суммируем баллы и попытки
    total_points = user_tasks['points'].sum()
    total_attempts = user_tasks['attempts'].sum()

    if total_attempts == 0:
        return total_points, 0, 0

    # Среднее количество баллов за одну попытку
    avg_points_per_attempt = round(total_points / total_attempts, 2)

    return  avg_points_per_attempt

def get_most_productive_weekday(user_id, dataframes):
    """
    Определение самого продуктивного дня недели по баллам
    roductive_day: самый продуктивный день недели
    - day_points: словарь с баллами по дням недели
    - avg_points_per_day: среднее количество баллов в день
    - max_points: баллы в самый продуктивный день
    - percent_above_avg: на сколько процентов баллы в продуктивный день больше среднего
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return None, {}, 0, 0, 0

    user_answers_df = dataframes['user_answers']

    # Фильтруем по пользователю
    user_tasks = user_answers_df[user_answers_df['user_id'] == user_id].copy()

    if len(user_tasks) == 0 or 'submitted_at' not in user_tasks.columns:
        return None, {}, 0, 0, 0

    # Преобразуем submitted_at в datetime
    user_tasks['submitted_at'] = pd.to_datetime(user_tasks['submitted_at'])

    # Определяем день недели (0 = Пн, 6 = Вс)
    user_tasks['weekday'] = user_tasks['submitted_at'].dt.weekday

    # Словарь с названиями дней недели
    weekday_names = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    # Группируем баллы по дням недели
    points_by_weekday = user_tasks.groupby('weekday')['points'].sum()

    # Заполняем нулями дни, в которые не было активности
    day_points = {}
    for day_num in range(7):
        day_name = weekday_names[day_num]
        points = points_by_weekday.get(day_num, 0)
        day_points[day_name] = points

    # Считаем среднее количество баллов в день (учитываем только дни с активностью)
    active_days = points_by_weekday[points_by_weekday > 0]
    if len(active_days) == 0:
        return None, day_points, 0, 0, 0

    avg_points_per_day = active_days.mean()

    # Находим самый продуктивный день
    max_day_num = points_by_weekday.idxmax()
    max_points = points_by_weekday.max()
    most_productive_day = weekday_names[max_day_num]

    # На сколько процентов больше среднего
    if avg_points_per_day > 0:
        percent_above_avg = round((max_points - avg_points_per_day) / avg_points_per_day * 100, 2)
    else:
        percent_above_avg = 0

    return most_productive_day, day_points, round(avg_points_per_day, 2), max_points, percent_above_avg


def get_most_productive_hour(user_id, dataframes):
    """
    Определение самого продуктивного времени дня по баллам
    Возвращает:
    - most_productive_hour: самый продуктивный час (0-23)
    - time_period: период дня (Утро/День/Вечер/Ночь)
    - hour_points: словарь с баллами по часам
    - max_points: баллы в самый продуктивный час
    - time_distribution: распределение баллов по периодам дня
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return None, None, {}, 0, {}

    user_answers_df = dataframes['user_answers']

    # Фильтруем по пользователю
    user_tasks = user_answers_df[user_answers_df['user_id'] == user_id].copy()

    if len(user_tasks) == 0 or 'submitted_at' not in user_tasks.columns:
        return None, None, {}, 0, {}

    # Преобразуем submitted_at в datetime
    user_tasks['submitted_at'] = pd.to_datetime(user_tasks['submitted_at'])

    # Определяем час отправки
    user_tasks['hour'] = user_tasks['submitted_at'].dt.hour

    # Группируем баллы по часам
    points_by_hour = user_tasks.groupby('hour')['points'].sum()

    # Заполняем нулями часы, в которые не было активности
    hour_points = {}
    for hour in range(24):
        points = points_by_hour.get(hour, 0)
        hour_points[hour] = points

    # Находим самый продуктивный час
    if points_by_hour.sum() > 0:
        most_productive_hour = points_by_hour.idxmax()
        max_points = points_by_hour.max()
    else:
        most_productive_hour = None
        max_points = 0

    # Определяем период дня
    def get_time_period(hour):
        if 6 <= hour < 12:
            return 'Утро'
        elif 12 <= hour < 18:
            return 'День'
        elif 18 <= hour < 24:
            return 'Вечер'
        else:
            return 'Ночь'

    time_period = get_time_period(most_productive_hour) if most_productive_hour is not None else None

    # Распределение баллов по периодам дня
    user_tasks['time_period'] = user_tasks['hour'].apply(get_time_period)
    time_distribution = user_tasks.groupby('time_period')['points'].sum().to_dict()

    # Заполняем нулями отсутствующие периоды
    for period in ['Утро', 'День', 'Вечер', 'Ночь']:
        if period not in time_distribution:
            time_distribution[period] = 0

    return most_productive_hour, time_period, hour_points, max_points, time_distribution


def get_user_most_active_week(dataframes, user_id):
    """
    Вычисляет самую активную неделю для пользователя
    (посещённые семинары + решённые домашки)
    Возвращает:
    tuple: (year, week, total_activities, seminars_count, homeworks_count)
           или None если данных нет
    """

    all_activities = []

    # 1. Семинары из wk_media_view_sessions
    if 'media_view_sessions' in dataframes:
        media_df = dataframes['media_view_sessions']

        user_seminars = media_df[
            _viewer_mask(media_df, user_id) &
            (media_df['resource_type'] == 'Group')
        ].copy()

        if not user_seminars.empty and 'started_at' in user_seminars.columns:
            user_seminars['timestamp'] = pd.to_datetime(user_seminars['started_at'])
            user_seminars['activity_type'] = 'seminar'
            all_activities.append(user_seminars[['timestamp', 'activity_type']])

    # 2. Домашки из user_answers через users_courses
    if 'user_answers' in dataframes and 'user_courses' in dataframes:
        answers_df = dataframes['user_answers']
        courses_df = dataframes['user_courses']

        # Получаем курсы пользователя
        user_courses = courses_df[courses_df['user_id'] == user_id]

        if not user_courses.empty and 'id' in user_courses.columns:
            user_course_ids = user_courses['id'].unique()

            # Находим решённые домашки
            mask = (
                answers_df['users_course_id'].isin(user_course_ids) &
                (answers_df['solved'] == 1)
            )
            if 'resource_type' in answers_df.columns:
                mask &= answers_df['resource_type'] == 'Homework'
            user_homeworks = answers_df[mask].copy()

            if not user_homeworks.empty and 'submitted_at' in user_homeworks.columns:
                user_homeworks['timestamp'] = pd.to_datetime(user_homeworks['submitted_at'])
                user_homeworks['activity_type'] = 'homework'
                all_activities.append(user_homeworks[['timestamp', 'activity_type']])

    # 3. Агрегация по неделям и поиск максимума
    if all_activities:
        combined = pd.concat(all_activities, ignore_index=True)

        combined['year'] = combined['timestamp'].dt.isocalendar().year
        combined['week'] = combined['timestamp'].dt.isocalendar().week

        # Группируем и считаем количество по типам
        weekly = combined.groupby(['year', 'week', 'activity_type']).size().unstack(fill_value=0)
        weekly['total'] = weekly.sum(axis=1)

        # Находим неделю с максимальной активностью
        max_idx = weekly['total'].idxmax()
        max_row = weekly.loc[max_idx]

        seminars_count = int(max_row.get('seminar', 0))
        homeworks_count = int(max_row.get('homework', 0))
        total = int(max_row['total'])

        return max_idx[0], max_idx[1], total, seminars_count, homeworks_count

    return None


def get_user_most_active_season(dataframes, user_id):
    """
    Вычисляет самый активный сезон для пользователя
    (посещённые семинары + решённые домашки)
    Returns:
    tuple: (season,total_activities, seminars_count, homeworks_count)
    """

    def get_season(month):
        if month in [12, 1, 2]:
            return 'Зима'
        elif month in [3, 4, 5]:
            return 'Весна'
        elif month in [6, 7, 8]:
            return 'Лето'
        else:
            return 'Осень'

    all_activities = []

    # 1. Семинары из media_view_sessions
    if 'media_view_sessions' in dataframes:
        media_df = dataframes['media_view_sessions']
        if 'viewer_id' in media_df.columns and 'resource_type' in media_df.columns:
            user_seminars = media_df[
                _viewer_mask(media_df, user_id) &
                (media_df['resource_type'] == 'Group')
            ].copy()

            if not user_seminars.empty and 'started_at' in user_seminars.columns:
                user_seminars['timestamp'] = pd.to_datetime(user_seminars['started_at'])
                user_seminars['activity_type'] = 'seminar'
                all_activities.append(user_seminars[['timestamp', 'activity_type']])

    # 2. Домашки через wk_users_courses_actions (если есть связь)
    if 'wk_users_courses_actions' in dataframes and 'user_courses' in dataframes:
        actions_df = dataframes['wk_users_courses_actions']
        courses_df = dataframes['user_courses']

        # Ищем курсы пользователя (предполагаем, что user_id есть в users_courses)
        if 'user_id' in courses_df.columns:
            user_courses = courses_df[courses_df['user_id'] == user_id]
        else:
            # Если нет user_id, пробуем найти через другие таблицы
            user_courses = pd.DataFrame()

        if not user_courses.empty and 'id' in user_courses.columns:
            user_course_ids = user_courses['id'].unique()

            # Фильтруем действия типа user_answer (1)
            user_homeworks = actions_df[
                (actions_df['users_course_id'].isin(user_course_ids)) &
                (actions_df['action'] == 1)  # 1: 'user_answer'
            ].copy()

            if not user_homeworks.empty and 'created_at' in user_homeworks.columns:
                user_homeworks['timestamp'] = pd.to_datetime(user_homeworks['created_at'])
                user_homeworks['activity_type'] = 'homework'
                all_activities.append(user_homeworks[['timestamp', 'activity_type']])

    # 3. Агрегация по сезонам
    if all_activities:
        combined = pd.concat(all_activities, ignore_index=True)

        # Добавляем временные метрики
        combined['year'] = combined['timestamp'].dt.year
        combined['month'] = combined['timestamp'].dt.month
        combined['season'] = combined['month'].apply(get_season)

        # Группируем по сезонам
        seasonal = combined.groupby(['season', 'activity_type']).size().unstack(fill_value=0)
        seasonal['total'] = seasonal.sum(axis=1)

        if not seasonal.empty:
            # Находим сезон с максимальной активностью
            max_idx = seasonal['total'].idxmax()
            max_row = seasonal.loc[max_idx]

            season = max_idx  # индекс — название сезона (строка)
            seminars_count = int(max_row.get('seminar', 0))
            homeworks_count = int(max_row.get('homework', 0))
            total = int(max_row['total'])

            return season, total, seminars_count, homeworks_count, seasonal

    return None

def get_productive_periods_of_year(user_id, dataframes):
    """
    Определение самого продуктивного и непродуктивного времени за год
    Возвращает:
    - most_productive_month: самый продуктивный месяц
    - least_productive_month: самый непродуктивный месяц
    - most_productive_season: самый продуктивный сезон
    - least_productive_season: самый непродуктивный сезон
    - monthly_stats: статистика по месяцам
    - seasonal_stats: статистика по сезонам
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return None, None, None, None, {}, {}

    user_answers = dataframes['user_answers'][
        dataframes['user_answers']['user_id'] == user_id
    ].copy()

    if len(user_answers) == 0 or 'submitted_at' not in user_answers.columns:
        return None, None, None, None, {}, {}

    # Преобразуем даты
    user_answers['submitted_at'] = pd.to_datetime(user_answers['submitted_at'])

    # Определяем месяц и сезон
    user_answers['month'] = user_answers['submitted_at'].dt.month
    user_answers['month_name'] = user_answers['submitted_at'].dt.strftime('%B')

    # Названия месяцев на русском
    month_names_ru = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }

    # Определяем сезон
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Зима'
        elif month in [3, 4, 5]:
            return 'Весна'
        elif month in [6, 7, 8]:
            return 'Лето'
        else:
            return 'Осень'

    user_answers['season'] = user_answers['month'].apply(get_season)

    # Группируем по месяцам
    monthly_points = user_answers.groupby('month')['points'].sum()
    monthly_tasks = user_answers.groupby('month').size()

    # Статистика по месяцам
    monthly_stats = {}
    for month in range(1, 13):
        month_name = month_names_ru[month]
        points = monthly_points.get(month, 0)
        tasks = monthly_tasks.get(month, 0)

        if tasks > 0:
            avg_points_per_task = round(points / tasks, 2)
        else:
            avg_points_per_task = 0

        monthly_stats[month_name] = {
            'points': int(points),
            'tasks': int(tasks),
            'avg_points_per_task': avg_points_per_task
        }

    # Группируем по сезонам
    seasonal_points = user_answers.groupby('season')['points'].sum()
    seasonal_tasks = user_answers.groupby('season').size()

    # Статистика по сезонам
    seasonal_stats = {}
    seasons = ['Зима', 'Весна', 'Лето', 'Осень']
    for season in seasons:
        points = seasonal_points.get(season, 0)
        tasks = seasonal_tasks.get(season, 0)

        if tasks > 0:
            avg_points_per_task = round(points / tasks, 2)
        else:
            avg_points_per_task = 0

        seasonal_stats[season] = {
            'points': int(points),
            'tasks': int(tasks),
            'avg_points_per_task': avg_points_per_task
        }

    # Находим самый продуктивный и непродуктивный месяц (только среди месяцев с активностью)
    active_months = {k: v for k, v in monthly_stats.items() if v['tasks'] > 0}

    if active_months:
        most_productive_month = max(active_months.items(), key=lambda x: x[1]['points'])
        least_productive_month = min(active_months.items(), key=lambda x: x[1]['points'])
    else:
        most_productive_month = (None, {'points': 0, 'tasks': 0})
        least_productive_month = (None, {'points': 0, 'tasks': 0})

    # Самый продуктивный и непродуктивный сезон
    active_seasons = {k: v for k, v in seasonal_stats.items() if v['tasks'] > 0}

    if active_seasons:
        most_productive_season = max(active_seasons.items(), key=lambda x: x[1]['points'])
        least_productive_season = min(active_seasons.items(), key=lambda x: x[1]['points'])
    else:
        most_productive_season = (None, {'points': 0, 'tasks': 0})
        least_productive_season = (None, {'points': 0, 'tasks': 0})

    return (most_productive_month, least_productive_month,
            most_productive_season, least_productive_season,
            monthly_stats, seasonal_stats)

def get_time_from_webinar_to_homework(user_id, dataframes):
    """
    Расчёт среднего времени между просмотром вебинара и выполнением домашки
    Возвращает:
    - avg_time_hours: среднее время в часах
    - avg_time_str: строковое представление среднего времени
    - fast_start_percent: процент домашек, начатых в течение 24 часов после вебинара
    - detail: детальная информация по каждой связке вебинар-домашка
    """

    # Получаем просмотры вебинаров
    webinar_views = []

    # Из media_view_sessions
    if 'media_view_sessions' in dataframes:
        media_views = dataframes['media_view_sessions'][
            _viewer_mask(dataframes['media_view_sessions'], user_id)
        ].copy()

        if len(media_views) > 0 and 'started_at' in media_views.columns:
            media_views['view_time'] = pd.to_datetime(media_views['started_at'])
            media_views['resource_type'] = media_views['resource_type'].fillna('unknown')
            webinar_views.append(media_views[['view_time', 'resource_id', 'resource_type']])

    # Из user_lessons
    if 'user_lessons' in dataframes and 'lessons' in dataframes:
        user_lessons = dataframes['user_lessons'][
            dataframes['user_lessons']['user_id'] == user_id
        ].copy()

        if len(user_lessons) > 0 and 'video_visited' in user_lessons.columns:
            # Находим уроки с просмотренным видео
            viewed_lessons = user_lessons[user_lessons['video_visited'] == True]

            if len(viewed_lessons) > 0:
                # Джойним с lessons для получения course_id
                lessons_df = dataframes['lessons'][['id', 'course_id']]
                viewed_lessons = viewed_lessons.merge(
                    lessons_df,
                    left_on='lesson_id',
                    right_on='id',
                    how='left'
                )

                # Определяем время просмотра
                time_col = None
                if 'updated_at' in viewed_lessons.columns:
                    time_col = 'updated_at'
                elif 'created_at' in viewed_lessons.columns:
                    time_col = 'created_at'

                if time_col:
                    webinar_views_data = viewed_lessons[['lesson_id', 'course_id', time_col]].copy()
                    webinar_views_data['view_time'] = pd.to_datetime(webinar_views_data[time_col])
                    webinar_views_data['resource_type'] = 'lesson'
                    webinar_views_data = webinar_views_data.rename(columns={'lesson_id': 'resource_id'})
                    webinar_views.append(webinar_views_data[['view_time', 'resource_id', 'resource_type', 'course_id']])

    if len(webinar_views) == 0:
        print("Нет данных о просмотрах вебинаров")
        return 0, "0 часов", 0, pd.DataFrame()

    # Объединяем все просмотры
    all_webinar_views = pd.concat(webinar_views, ignore_index=True, sort=False)
    all_webinar_views = all_webinar_views.sort_values('view_time')

    # Получаем выполнения домашек
    if 'user_answers' not in dataframes:
        print("Нет данных о домашних заданиях")
        return 0, "0 часов", 0, pd.DataFrame()

    homeworks = dataframes['user_answers'][
        dataframes['user_answers']['user_id'] == user_id
    ].copy()

    if len(homeworks) == 0 or 'submitted_at' not in homeworks.columns:
        print("Нет данных о выполненных домашних заданиях")
        return 0, "0 часов", 0, pd.DataFrame()

    homeworks['homework_time'] = pd.to_datetime(homeworks['submitted_at'])
    homeworks = homeworks.sort_values('homework_time')

    # Связываем каждый просмотр вебинара с ближайшей последующей домашкой
    matches = []

    for _, webinar in all_webinar_views.iterrows():
        webinar_time = webinar['view_time']

        # Ищем домашки, сделанные после этого вебинара
        future_homeworks = homeworks[homeworks['homework_time'] > webinar_time]

        if len(future_homeworks) > 0:
            # Берём ближайшую домашку
            next_homework = future_homeworks.iloc[0]
            time_diff = next_homework['homework_time'] - webinar_time

            matches.append({
                'webinar_time': webinar_time,
                'homework_time': next_homework['homework_time'],
                'time_diff_hours': time_diff.total_seconds() / 3600,
                'resource_id': webinar.get('resource_id', None),
                'course_id': webinar.get('course_id', None),
                'task_id': next_homework.get('task_id', None)
            })

    if len(matches) == 0:
        print("Не найдено домашек, выполненных после просмотра вебинаров")
        return 0, "0 часов", 0, pd.DataFrame()

    matches_df = pd.DataFrame(matches)

    # Убираем аномально большие промежутки (> 7 дней) - вероятно, это не связано
    matches_df = matches_df[matches_df['time_diff_hours'] <= 168]  # 7 дней

    if len(matches_df) == 0:
        return 0, "0 часов", 0, pd.DataFrame()

    # Считаем статистику
    avg_time_hours = matches_df['time_diff_hours'].mean()

    # Форматируем время
    if avg_time_hours < 1:
        avg_time_str = f"{int(avg_time_hours * 60)} минут"
    elif avg_time_hours < 24:
        hours = int(avg_time_hours)
        minutes = int((avg_time_hours - hours) * 60)
        avg_time_str = f"{hours} ч {minutes} мин"
    else:
        days = int(avg_time_hours / 24)
        hours = int(avg_time_hours % 24)
        avg_time_str = f"{days} дн {hours} ч"

    # Процент домашек, начатых в течение 24 часов
    fast_starts = len(matches_df[matches_df['time_diff_hours'] <= 24])
    fast_start_percent = round(fast_starts / len(matches_df) * 100, 1)

    # Медиана
    median_time_hours = matches_df['time_diff_hours'].median()

    return avg_time_hours, avg_time_str, fast_start_percent, matches_df, median_time_hours

# вспомогательная
def user_data_dateformat(users_id, user_data, requested_column, dataframes, utc=False):
    """Конвертация времени в локальный часовой пояс пользователя"""
    from pytz import timezone, UTC
    import pandas as pd

    user_id = users_id
    user_data = user_data.copy()

    user_data['time'] = pd.to_datetime(user_data[requested_column])

    students = dataframes['students_of_interest']
    tz = timezone(students[students['id'] == user_id]['timezone'].iloc[0])

    if utc == False:
        msk = timezone('Europe/Moscow')
        if user_data['time'].dt.tz is not None:
            user_data['time'] = user_data['time'].dt.tz_convert(msk)
        else:
            user_data['time'] = user_data['time'].apply(lambda x: msk.localize(x) if pd.notna(x) else x)
    else:
        if user_data['time'].dt.tz is None:
            user_data['time'] = user_data['time'].dt.tz_localize(UTC)
        else:
            user_data['time'] = user_data['time'].dt.tz_convert(UTC)

    user_data['local_time'] = user_data['time'].dt.tz_convert(tz)
    user_data['date'] = user_data['local_time'].dt.date
    return user_data

def after_midnight_tasks(user_id, dataframes):
    """Количество действий после полуночи (00:00-05:00)"""
    user_data = dataframes['wk_users_courses_actions'][
        dataframes['wk_users_courses_actions']['user_id'] == user_id
    ].copy()

    user_data = user_data_dateformat(user_id, user_data, 'created_at', dataframes)
    after_mn_tasks = user_data['local_time'].dt.hour.between(0, 5).sum()
    return after_mn_tasks


def points_gain_through_time(user_id, dataframes):
    """Накопленные баллы по дням"""
    user_data = dataframes['user_answers'][
        dataframes['user_answers']['user_id'] == user_id
    ].copy()

    user_data = user_data_dateformat(user_id, user_data, 'submitted_at', dataframes, utc=True)

    points_dots = (
        user_data[user_data['points'] != 0]
        .groupby('date')['points']
        .sum()
        .reset_index()
    )

    points_dots['cumulative'] = points_dots['points'].cumsum()
    return points_dots


def uniformity_score(points_dots):
    """Показатель равномерности (0 - стабильно, >1 - нестабильно)"""
    import pandas as pd
    mean = points_dots['points'].mean()
    std = points_dots['points'].std()

    if pd.isna(mean) or mean == 0:
        return 1
    if pd.isna(std):
        return 1

    return std / mean


def performance_through_time(user_id, dataframes):
    """Успеваемость по урокам во времени"""
    user_data = dataframes['user_lessons'][
        dataframes['user_lessons']['user_id'] == user_id
    ].copy()

    user_data = user_data_dateformat(user_id, user_data, 'updated_at', dataframes, utc=True)
    user_data = user_data.dropna(subset=['wk_points']).reset_index(drop=True)
    user_data = user_data[['user_id', 'lesson_id', 'date', 'wk_points']]

    user_data = user_data.merge(
        dataframes['lessons'][['id', 'wk_max_points']],
        left_on='lesson_id',
        right_on='id',
        how='left'
    )

    user_data['grade'] = user_data['wk_points'] / user_data['wk_max_points']
    user_data = user_data.drop(columns=['id'])

    return user_data


def time_spent_watching(user_id, dataframes):
    """Время просмотра видео по месяцам (сек)"""
    import pandas as pd
    media = dataframes['media_view_sessions'].copy()

    media['viewer_id_clean'] = (
        media['viewer_id']
        .astype(str)
        .str.replace(',', '')
        .astype(float)
        .astype('Int64')
    )

    user_data = media[media['viewer_id_clean'] == user_id].copy()

    if user_data.empty:
        return pd.DataFrame({'month': [pd.NaT], 'time_spent_watching': [None]})

    user_data = user_data_dateformat(user_id, user_data, 'started_at', dataframes)
    user_data['month'] = user_data['local_time'].dt.to_period('M')
    user_data['time_spent_watching'] = user_data['segment_size'] * user_data['viewed_segments_count']

    result = user_data.groupby('month', as_index=False)['time_spent_watching'].sum()
    return result


def time_spent_answering(user_id, dataframes):
    """Время на ответы по типам ресурсов по месяцам (сек)"""
    user_data = dataframes['user_answers'][
        dataframes['user_answers']['user_id'] == user_id
    ].copy()

    user_data = user_data_dateformat(user_id, user_data, 'created_at', dataframes, utc=True)
    user_data = user_data.rename(columns={'local_time': 'local_start'})

    user_data = user_data_dateformat(user_id, user_data, 'submitted_at', dataframes, utc=True)
    user_data = user_data.rename(columns={'local_time': 'local_finish'})

    user_data['month'] = user_data['local_finish'].dt.to_period('M')
    user_data['time_spent'] = (user_data['local_finish'] - user_data['local_start']).dt.total_seconds()
    user_data['time_spent'] = user_data['time_spent'].clip(upper=3600)

    result = (
        user_data
        .groupby(['month', 'resource_type'])['time_spent']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    return result






def plot_monthly_activity(user_id, dataframes, user_activity_stats=None):
    """
    График распределения времени по типам активности по месяцам.
    """
    if user_activity_stats is None:
        # Рассчитываем активности
        watching = time_spent_watching(user_id, dataframes)
        answering = time_spent_answering(user_id, dataframes)

        # Объединяем
        watching['month'] = watching['month'].astype(str)
        answering['month'] = answering['month'].astype(str)

        activity = answering.merge(
            watching,
            on='month',
            how='outer'
        ).fillna(0)

        # Переводим в минуты
        for col in ['Homework', 'Lesson', 'Training']:
            if col in activity.columns:
                activity[col] = activity[col] / 60

        if 'time_spent_watching' in activity.columns:
            activity['time_spent_watching'] = activity['time_spent_watching'] / 60
    else:
        activity = user_activity_stats[user_activity_stats['user_id'] == user_id].copy()

    if activity.empty or (activity[['Homework', 'Lesson', 'Training', 'time_spent_watching']].sum().sum() == 0):
        print(f"Нет данных об активности для пользователя {user_id}")
        return None

    # Убираем NaT строки
    activity = activity[activity['month'] != 'NaT']
    activity = activity.sort_values('month')

    fig = go.Figure()

    # Типы активностей
    traces = [
        ('Homework', 'Домашние задания', '#FF6B6B'),
        ('Lesson', 'Уроки', '#4ECDC4'),
        ('Training', 'Тренинги', '#45B7D1'),
        ('time_spent_watching', 'Просмотр видео', '#96CEB4')
    ]

    for col, name, color in traces:
        if col in activity.columns:
            fig.add_trace(go.Bar(
                x=activity['month'],
                y=activity[col],
                name=name,
                marker_color=color
            ))

    fig.update_layout(
        title=f'Распределение времени по месяцам (пользователь {user_id})',
        xaxis_title='Месяц',
        yaxis_title='Время (минуты)',
        barmode='stack',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig



def plot_user_comparison(dataframes, metric='points', top_n=10):
    """
    Сравнение пользователей по выбранной метрике.
    """
    if 'courses_stats' not in dataframes:
        print("Таблица 'courses_stats' не найдена")
        return None

    df = dataframes['courses_stats'].copy()

    if metric == 'points':
        df_sorted = df.nlargest(top_n, 'Набрал баллов')[['user_id', 'Набрал баллов', 'Регион']]
        title = f'Топ-{top_n} пользователей по набранным баллам'
        y_label = 'Набранные баллы'
        color_col = 'Набрал баллов'
    else:
        df_sorted = df.nlargest(top_n, 'Решал задач')[['user_id', 'Решал задач', 'Регион']]
        title = f'Топ-{top_n} пользователей по решённым задачам'
        y_label = 'Количество решённых задач'
        color_col = 'Решал задач'

    fig = px.bar(
        df_sorted,
        x='user_id',
        y=y_label,
        color=color_col,
        text=y_label,
        title=title,
        color_continuous_scale='Viridis',
        labels={'user_id': 'ID пользователя', y_label: y_label}
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(template='plotly_white')

    return fig



def plot_activity_pie(user_id, dataframes):
    """
    Круговая диаграмма распределения типов активности.
    """
    activity_types = {}

    # 1. Задачи из user_answers
    if 'user_answers' in dataframes:
        answers = dataframes['user_answers'][
            dataframes['user_answers']['user_id'] == user_id
        ]
        if not answers.empty:
            activity_types['Решение задач'] = len(answers[answers['solved'] == True])
            activity_types['Попытки решения'] = len(answers[answers['solved'] == False])

    # 2. Просмотр видео
    if 'media_view_sessions' in dataframes:
        media = dataframes['media_view_sessions']
        media['viewer_id_clean'] = media['viewer_id'].astype(str).str.replace(',', '').astype(float).astype('Int64')
        views = media[media['viewer_id_clean'] == user_id]
        if not views.empty:
            activity_types['Просмотр видео'] = len(views)

    # 3. Тренинги
    if 'user_trainings' in dataframes:
        trainings = dataframes['user_trainings'][
            dataframes['user_trainings']['user_id'] == user_id
        ]
        if not trainings.empty:
            activity_types['Тренинги'] = len(trainings)

    if not activity_types:
        print(f"Нет данных об активности для пользователя {user_id}")
        return None

    # Цвета для диаграммы
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

    fig = go.Figure(data=[go.Pie(
        labels=list(activity_types.keys()),
        values=list(activity_types.values()),
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='auto'
    )])

    fig.update_layout(
        title=f'Распределение активности (пользователь {user_id})',
        template='plotly_white'
    )

    return fig


def plot_badges_timeline(user_id, dataframes):
    """
    График получения достижений пользователя по времени.
    """
    if 'user_award_badges' not in dataframes:
        print("Таблица 'user_award_badges' не найдена")
        return None

    user_badges = dataframes['user_award_badges'][
        dataframes['user_award_badges']['user_id'] == user_id
    ].copy()

    if user_badges.empty:
        print(f"Нет достижений у пользователя {user_id}")
        return None

    # Преобразуем даты
    user_badges['created_at'] = pd.to_datetime(user_badges['created_at'])
    user_badges = user_badges.sort_values('created_at')

    # Накопленное количество достижений
    user_badges['cumulative_count'] = range(1, len(user_badges) + 1)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=user_badges['created_at'],
        y=user_badges['cumulative_count'],
        mode='lines+markers',
        name='Накопленные достижения',
        line=dict(color='gold', width=3),
        marker=dict(size=10, symbol='star')
    ))

    fig.update_layout(
        title=f'Динамика получения достижений (пользователь {user_id})',
        xaxis_title='Дата',
        yaxis_title='Количество достижений',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig

def create_summary_table(dataframes):
    """
    Создаёт сводную таблицу со всеми метриками для всех пользователей.

    Параметры:
    - dataframes: словарь с датафреймами
    """
    if 'students_of_interest' not in dataframes:
        print("Таблица 'students_of_interest' не найдена")
        return None

    summary = dataframes['students_of_interest'][['id', 'Регион', 'Муниципалитет', 'Школа']].copy()
    summary.rename(columns={'id': 'user_id'}, inplace=True)

    # Добавляем метрики
    for user_id in summary['user_id']:
        # Базовые метрики
        summary.loc[summary['user_id'] == user_id, 'набрано_баллов'] = calculate_total_points_earned_from_tasks(user_id, dataframes)
        summary.loc[summary['user_id'] == user_id, 'среднее_попыток'] = calculate_avg_attempts_per_task(user_id, dataframes)
        summary.loc[summary['user_id'] == user_id, 'процент_решенных'] = calculate_solved_tasks_ratio(user_id, dataframes) * 100
        summary.loc[summary['user_id'] == user_id, 'процент_уроков'] = calculate_completed_to_opened_lessons_ratio(user_id, dataframes) * 100
        summary.loc[summary['user_id'] == user_id, 'достижений'] = get_user_awards_count(user_id, dataframes)
        summary.loc[summary['user_id'] == user_id, 'действия_после_полуночи'] = after_midnight_tasks(user_id, dataframes)

        # Равномерность
        points_data = points_gain_through_time(user_id, dataframes)
        summary.loc[summary['user_id'] == user_id, 'равномерность'] = uniformity_score(points_data)

    # Округляем числовые колонки
    numeric_cols = ['набрано_баллов', 'среднее_попыток', 'процент_решенных',
                    'процент_уроков', 'равномерность']
    for col in numeric_cols:
        if col in summary.columns:
            summary[col] = summary[col].round(2)

    return summary

def plot_activity_heatmap(user_id, dataframes):
    """
    Тепловая карта активности: дни недели vs часы.
    """
    if 'user_answers' not in dataframes:
        print("Таблица 'user_answers' не найдена")
        return None

    user_answers = dataframes['user_answers'][
        dataframes['user_answers']['user_id'] == user_id
    ].copy()

    if user_answers.empty or 'submitted_at' not in user_answers.columns:
        print(f"Нет данных о решениях для пользователя {user_id}")
        return None

    # Преобразуем время
    user_answers['submitted_at'] = pd.to_datetime(user_answers['submitted_at'])

    # Дни недели (0=пн, 6=вс) и часы
    user_answers['weekday'] = user_answers['submitted_at'].dt.weekday
    user_answers['hour'] = user_answers['submitted_at'].dt.hour

    # Создаём пустую матрицу 7x24
    activity_matrix = np.zeros((7, 24))

    # Заполняем матрицу вручную
    for _, row in user_answers.iterrows():
        wd = row['weekday']
        h = row['hour']
        points = row['points'] if pd.notna(row['points']) else 0
        activity_matrix[wd, h] += points

    # Названия дней
    day_names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

    fig = px.imshow(
        activity_matrix,
        title=f'Тепловая карта активности (пользователь {user_id})',
        labels=dict(x='Час дня', y='День недели', color='Баллы'),
        x=list(range(24)),
        y=day_names,
        color_continuous_scale='YlOrRd',
        aspect='auto'
    )

    fig.update_layout(template='plotly_white')

    return fig

def plot_cumulative_points(user_id, dataframes):
    """
    Интерактивный график накопления баллов пользователя.
    """
    points_dots = points_gain_through_time(user_id, dataframes)

    if points_dots.empty:
        print(f"Нет данных о баллах для пользователя {user_id}")
        return None

    fig = go.Figure()

    # Столбцы - баллы за день
    fig.add_trace(go.Bar(
        x=points_dots['date'],
        y=points_dots['points'],
        name='Баллы за день',
        marker_color='lightblue',
        opacity=0.7
    ))

    # Линия - накопленные баллы
    fig.add_trace(go.Scatter(
        x=points_dots['date'],
        y=points_dots['cumulative'],
        mode='lines+markers',
        name='Накопленные баллы',
        line=dict(color='darkblue', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title=f'История успеваемости (пользователь {user_id})',
        xaxis_title='Дата',
        yaxis_title='Баллы',
        hovermode='x unified',
        template='plotly_white',
        xaxis_rangeslider_visible=True
    )

    return fig


def plot_performance(user_id, dataframes):
    """
    График успеваемости (оценки за уроки).
    """
    performance_data = performance_through_time(user_id, dataframes)

    if performance_data.empty:
        print(f"Нет данных об успеваемости для пользователя {user_id}")
        return None

    # Сортируем по дате
    performance_data = performance_data.sort_values('date')

    # Добавляем сглаженный тренд
    performance_data['grade_smooth'] = performance_data['grade'].ewm(span=5, min_periods=1).mean()

    fig = go.Figure()

    # Столбцы - оценка за день
    fig.add_trace(go.Bar(
        x=performance_data['date'],
        y=performance_data['grade'],
        name='Оценка за урок',
        marker_color='lightgreen',
        opacity=0.6
    ))

    # Линия тренда
    fig.add_trace(go.Scatter(
        x=performance_data['date'],
        y=performance_data['grade_smooth'],
        mode='lines',
        name='Тренд успеваемости',
        line=dict(color='darkgreen', width=3)
    ))

    fig.update_layout(
        title=f'Успеваемость по урокам (пользователь {user_id})',
        xaxis_title='Дата',
        yaxis_title='Оценка (0-1)',
        yaxis_range=[0, 1.1],
        hovermode='x unified',
        template='plotly_white'
    )

    return fig

def generate_full_report(user_id, dataframes):
    """
    Генерирует полный отчёт со всеми визуализациями.
    """
    print(f"Генерация отчёта для пользователя {user_id}...")

    # Строим графики по одному (без предварительного расчёта всех пользователей)
    print("\n1. График накопления баллов...")
    fig1 = plot_cumulative_points(user_id, dataframes)

    print("2. График успеваемости...")
    fig2 = plot_performance(user_id, dataframes)

    print("3. График месячной активности...")
    fig3 = plot_monthly_activity(user_id, dataframes)

    print("4. Тепловая карта активности...")
    fig4 = plot_activity_heatmap(user_id, dataframes)

    print("5. Круговая диаграмма активности...")
    fig5 = plot_activity_pie(user_id, dataframes)

    print("6. Динамика достижений...")
    fig6 = plot_badges_timeline(user_id, dataframes)

    # Показываем графики
    for fig, name in zip([fig1, fig2, fig3, fig4, fig5, fig6],
                         ['Накопление баллов', 'Успеваемость', 'Месячная активность',
                          'Тепловая карта', 'Активность', 'Достижения']):
        if fig is not None:
            fig.show()
        else:
            print(f"  ⚠ График '{name}' не построен (нет данных)")

    return {
        'cumulative_points': fig1,
        'performance': fig2,
        'monthly_activity': fig3,
        'heatmap': fig4,
        'activity_pie': fig5,
        'badges_timeline': fig6
    }