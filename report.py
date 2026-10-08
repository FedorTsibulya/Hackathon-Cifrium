import metrics

def get_function_description(func):
    """Извлекает описание функции из docstring (первая строка)"""
    if func.__doc__:
        desc = func.__doc__.strip().split('\n')[0].strip('.')
        return desc
    return func.__name__

def format_value(value):
    """Форматирует значение для вывода"""
    if isinstance(value, float):
        if 0 <= value <= 1 and value != round(value):
            return f"{value:.1%}"
        else:
            return f"{value:.2f}"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, tuple) or isinstance(value, list):
        return str(value)
    elif value is None:
        return "Нет данных"
    else:
        return str(value)

def generate_report(user_id, dataframes):
    """Генерирует полный отчёт для пользователя"""
    
    print("=" * 80)
    print(f"МЕТРИКИ ДЛЯ ПОЛЬЗОВАТЕЛЯ {user_id}")
    print("=" * 80)

    # МЕТРИКИ ДИНЫ
    print("\n📚 МЕТРИКИ УСПЕВАЕМОСТИ")
    print("-" * 50)

    funcs_dina = [
        metrics.calculate_course_completion_percent,
        metrics.calculate_earned_points_ratio,
        metrics.calculate_started_tasks_ratio,
        metrics.calculate_solved_tasks_ratio,
        metrics.calculate_solved_to_started_ratio,
        metrics.calculate_avg_attempts_per_task,
        metrics.calculate_max_attempts_per_task,
        metrics.calculate_total_points_earned_from_tasks,
        metrics.calculate_videos_started_count,
        metrics.calculate_avg_watch_percent,
        metrics.calculate_watched_to_started_videos_ratio,
        metrics.calculate_lessons_with_video_viewed_count,
        metrics.calculate_completed_lessons_count,
        metrics.calculate_completed_to_opened_lessons_ratio,
        metrics.calculate_max_tasks_in_course
    ]

    # Метрики-доли (0..1) выводим в процентах; метрика 1 уже возвращает проценты
    ratio_funcs = {
        metrics.calculate_earned_points_ratio,
        metrics.calculate_started_tasks_ratio,
        metrics.calculate_solved_tasks_ratio,
        metrics.calculate_solved_to_started_ratio,
        metrics.calculate_avg_watch_percent,
        metrics.calculate_watched_to_started_videos_ratio,
        metrics.calculate_completed_to_opened_lessons_ratio,
    }

    for func in funcs_dina:
        try:
            value = func(user_id, dataframes)
            desc = get_function_description(func)
            if func is metrics.calculate_course_completion_percent:
                shown = f"{value:.1f}%"
            elif func in ratio_funcs:
                shown = f"{value:.1%}"
            else:
                shown = format_value(value)
            print(f"  • {desc}: {shown}")
        except Exception as e:
            print(f"  • {get_function_description(func)}: ОШИБКА - {e}")

    # МЕТРИКИ ПОЛИНЫ
    print("\n🏆 МЕТРИКИ СРАВНЕНИЯ И АКТИВНОСТИ")
    print("-" * 50)

    try:
        value = metrics.get_better_than_percent_in_city(user_id, dataframes)
        desc = get_function_description(metrics.get_better_than_percent_in_city)
        if value is not None:
            print(f"  • {desc}: {value}%")
        else:
            print(f"  • {desc}: Нет данных")
    except Exception as e:
        print(f"  • Лучше, чем % ребят из твоего города: ОШИБКА - {e}")

    try:
        value = metrics.get_lessons_watched_count(user_id, dataframes)
        desc = get_function_description(metrics.get_lessons_watched_count)
        print(f"  • {desc}: {value}")
    except Exception as e:
        print(f"  • Количество посещённых лекций и вебинаров: ОШИБКА - {e}")

    try:
        value = metrics.get_studied_themes_count(user_id, dataframes)
        desc = get_function_description(metrics.get_studied_themes_count)
        print(f"  • {desc}: {value}")
    except Exception as e:
        print(f"  • Количество изученных тем: ОШИБКА - {e}")

    try:
        count, avg_score = metrics.get_trainings_completed_info(user_id, dataframes)
        print(f"  • Количество выполненных тренингов: {count}")
        print(f"  • Средний балл за тренинги: {avg_score:.2f}")
    except Exception as e:
        print(f"  • Информация о тренингах: ОШИБКА - {e}")

    try:
        value = metrics.get_max_time_spent_on_task(user_id, dataframes)
        if value is not None:
            if hasattr(value, 'total_seconds'):
                total_min = int(value.total_seconds() // 60)
                value = f"{total_min // 60} ч {total_min % 60} мин"
            print(f"  • Максимальное время, потраченное на одну задачу: {value}")
        else:
            print(f"  • Максимальное время, потраченное на одну задачу: Нет данных")
    except Exception as e:
        print(f"  • Максимальное время на задачу: ОШИБКА - {e}")

    try:
        value = metrics.get_webinars_total_duration_original_style(user_id, dataframes)
        if value is not None:
            print(f"  • Общая длительность просмотренных вебинаров: {value} сек")
        else:
            print(f"  • Общая длительность просмотренных вебинаров: Нет данных")
    except Exception as e:
        print(f"  • Длительность вебинаров: ОШИБКА - {e}")

    # МЕТРИКИ ЛЕНЫ
    print("\n⭐ МЕТРИКИ КАЧЕСТВА")
    print("-" * 50)

    try:
        value = metrics.get_user_awards_count(user_id, dataframes)
        desc = get_function_description(metrics.get_user_awards_count)
        print(f"  • {desc}: {value}")
    except Exception as e:
        print(f"  • Количество достижений: ОШИБКА - {e}")

    try:
        rate = metrics.get_first_attempt_success_rate(user_id, dataframes)
        print(f"  • Доля задач, решённых с первой попытки: {rate}%")
    except Exception as e:
        print(f"  • Доля задач с первой попытки: ОШИБКА - {e}")

    try:
        not_first_count, total_solved, rate = metrics.get_not_first_attempt_success_rate(user_id, dataframes)
        print(f"  • Доля задач, решённых НЕ с первой попытки: {rate}%")
    except Exception as e:
        print(f"  • Доля задач не с первой попытки: ОШИБКА - {e}")

    try:
        unsolved_count, total_tasks, rate = metrics.get_unsolved_tasks_count(user_id, dataframes)
        print(f"  • Доля нерешённых задач: {rate}%")
    except Exception as e:
        print(f"  • Доля нерешённых задач: ОШИБКА - {e}")

    try:
        value = metrics.get_avg_points_per_attempt(user_id, dataframes)
        print(f"  • Среднее количество баллов за одну попытку: {value}")
    except Exception as e:
        print(f"  • Среднее баллов за попытку: ОШИБКА - {e}")

    try:
        productive_day, day_points, avg_points, max_points, percent = metrics.get_most_productive_weekday(user_id, dataframes)
        if productive_day:
            print(f"  • Самый продуктивный день недели: {productive_day} ({max_points} баллов, на {percent}% выше среднего)")
        else:
            print(f"  • Самый продуктивный день недели: Нет данных")
    except Exception as e:
        print(f"  • Продуктивный день: ОШИБКА - {e}")

    try:
        productive_hour, time_period, hour_points, max_points, time_distribution = metrics.get_most_productive_hour(user_id, dataframes)
        if productive_hour is not None:
            print(f"  • Самый продуктивный час: {productive_hour}:00 ({time_period}) - {max_points} баллов")
        else:
            print(f"  • Самый продуктивный час: Нет данных")
    except Exception as e:
        print(f"  • Продуктивный час: ОШИБКА - {e}")

    try:
        result = metrics.get_user_most_active_week(dataframes, user_id)
        if result:
            year, week, total, seminars, homeworks = result
            print(f"  • Самая активная неделя: {year}-W{week:02d} (всего действий: {total})")
        else:
            print(f"  • Самая активная неделя: Нет данных")
    except Exception as e:
        print(f"  • Активная неделя: ОШИБКА - {e}")

    try:
        result = metrics.get_user_most_active_season(dataframes, user_id)
        if result:
            season, total, seminars, homeworks, _ = result
            print(f"  • Самый активный сезон: {season} (всего действий: {total})")
        else:
            print(f"  • Самый активный сезон: Нет данных")
    except Exception as e:
        print(f"  • Активный сезон: ОШИБКА - {e}")

    try:
        most_prod_month, least_prod_month, most_prod_season, least_prod_season, monthly_stats, seasonal_stats = metrics.get_productive_periods_of_year(user_id, dataframes)
        if most_prod_month[0]:
            print(f"  • Самый продуктивный месяц: {most_prod_month[0]} ({most_prod_month[1]['points']} баллов)")
            print(f"  • Самый непродуктивный месяц: {least_prod_month[0]} ({least_prod_month[1]['points']} баллов)")
        if most_prod_season[0]:
            print(f"  • Самый продуктивный сезон: {most_prod_season[0]} ({most_prod_season[1]['points']} баллов)")
            print(f"  • Самый непродуктивный сезон: {least_prod_season[0]} ({least_prod_season[1]['points']} баллов)")
    except Exception as e:
        print(f"  • Продуктивные периоды года: ОШИБКА - {e}")

    try:
        avg_hours, time_str, fast_percent, matches_df, median = metrics.get_time_from_webinar_to_homework(user_id, dataframes)
        if avg_hours > 0:
            print(f"  • Среднее время от вебинара до домашки: {time_str}")
            print(f"  • Домашек в течение 24 часов: {fast_percent}%")
        else:
            print(f"  • Время от вебинара до домашки: Нет данных")
    except Exception as e:
        print(f"  • Вебинар→домашка: ОШИБКА - {e}")

    # МЕТРИКИ ФЕДИ
    print("\n⏰ ТЕМПОРАЛЬНЫЕ МЕТРИКИ")
    print("-" * 50)

    try:
        value = metrics.after_midnight_tasks(user_id, dataframes)
        print(f"  • Количество действий после полуночи: {value}")
    except Exception as e:
        print(f"  • Действия после полуночи: ОШИБКА - {e}")

    try:
        points_data = metrics.points_gain_through_time(user_id, dataframes)
        value = metrics.uniformity_score(points_data)
        print(f"  • Равномерность накопления баллов: {value:.3f} (чем ближе к 0, тем стабильнее)")
    except Exception as e:
        print(f"  • Равномерность: ОШИБКА - {e}")

    print("\n📊 ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ")
    print("-" * 50)

    try:
        points_data = metrics.points_gain_through_time(user_id, dataframes)
        if not points_data.empty:
            print(f"  • Всего дней с активностью: {len(points_data)}")
            print(f"  • Всего накоплено баллов: {points_data['cumulative'].iloc[-1]:.1f}")
            print(f"  • Средний балл в активный день: {points_data['points'].mean():.1f}")
            print(f"  • Максимум баллов за один день: {points_data['points'].max():.1f}")
    except Exception as e:
        print(f"  • Анализ накопления баллов: ОШИБКА - {e}")

    try:
        perf_data = metrics.performance_through_time(user_id, dataframes)
        if not perf_data.empty:
            print(f"  • Средняя оценка за уроки: {perf_data['grade'].mean():.2f}")
    except Exception as e:
        print(f"  • Средняя оценка: ОШИБКА - {e}")

    try:
        watch_data = metrics.time_spent_watching(user_id, dataframes)
        if not watch_data.empty and watch_data['time_spent_watching'].iloc[0] is not None:
            total_min = watch_data['time_spent_watching'].sum() / 60
            print(f"  • Общее время просмотра видео: {total_min:.1f} минут")
    except Exception as e:
        print(f"  • Время просмотра: ОШИБКА - {e}")

    try:
        answer_data = metrics.time_spent_answering(user_id, dataframes)
        if not answer_data.empty:
            time_cols = [col for col in answer_data.columns if col != 'month']
            total_min = answer_data[time_cols].sum().sum() / 60
            print(f"  • Общее время на ответы: {total_min:.1f} минут")
    except Exception as e:
        print(f"  • Время на ответы: ОШИБКА - {e}")

    print("\n" + "=" * 80)
    print("ВЫВОД ЗАВЕРШЁН")
    print("=" * 80)