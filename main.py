import sys
from contextlib import redirect_stdout

from data_loader import *
from metrics import *
from report import generate_report

user_id = 665767

# ========== НАСТРОЙКИ ==========
SAVE_TEXT_REPORT = True      # Сохранять текстовый отчёт
SHOW_PLOTS = True            # Показывать графики (интерактивно)
SAVE_PLOTS_AS_HTML = True    # Сохранять графики в HTML файлы
# ================================

# 1. Текстовый отчёт
if SAVE_TEXT_REPORT:
    output_file = f"report_user_{user_id}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            generate_report(user_id, dataframes)
    print(f"✅ Текстовый отчёт сохранён: {output_file}")

# 2. Графики
if SHOW_PLOTS or SAVE_PLOTS_AS_HTML:
    print("\n📊 Генерация графиков...")
    
    # Создаём графики
    fig1 = plot_cumulative_points(user_id, dataframes)
    fig2 = plot_performance(user_id, dataframes)
    fig3 = plot_monthly_activity(user_id, dataframes)
    fig4 = plot_activity_heatmap(user_id, dataframes)
    fig5 = plot_activity_pie(user_id, dataframes)
    fig6 = plot_badges_timeline(user_id, dataframes)
    
    # Показываем
    if SHOW_PLOTS:
        for fig, name in zip([fig1, fig2, fig3, fig4, fig5, fig6],
                             ['Накопление баллов', 'Успеваемость', 'Месячная активность',
                              'Тепловая карта', 'Активность', 'Достижения']):
            if fig:
                fig.show()
    
    # Сохраняем в HTML
    if SAVE_PLOTS_AS_HTML:
        import os
        plots_dir = f"plots_user_{user_id}"
        os.makedirs(plots_dir, exist_ok=True)
        
        for fig, name in zip([fig1, fig2, fig3, fig4, fig5, fig6],
                             ['cumulative_points', 'performance', 'monthly_activity',
                              'heatmap', 'activity_pie', 'badges_timeline']):
            if fig:
                fig.write_html(f"{plots_dir}/{name}.html", include_plotlyjs="cdn")  # ~10 КБ вместо ~5 МБ
        print(f"✅ Графики сохранены в папку: {plots_dir}/")

print("\n🎉 Готово!")