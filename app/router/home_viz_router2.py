import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import io
from fastapi import APIRouter
from starlette.responses import StreamingResponse
from app.db.init import engine 
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# --- FastAPI Router ---
router = APIRouter()

# Set a professional plot style globally
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

@router.get('/chart_2', tags=['Visualizations'])
async def get_dashboard_stream():
    """
    Generate the dashboard of Average Salary by Job Title Over Time.
    """
    # Switch backend to 'Agg' for non-GUI server environments
    plt.switch_backend('Agg')

    try:
        with engine.connect() as conn:
            print("Database connection successful for dashboard.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        # Return the error directly
        return {"error": f"Database connection error: {e}"}

    fig, axes = plt.subplots(1, 1, figsize=(12, 7))

    # --- Plot: Average salary over time BY JOB TITLE ---
    query2 = """
    SELECT
        YEAR(s.from_date) AS salary_year,
        t.title,
        AVG(s.salary) AS avg_salary
    FROM
        salaries s
    JOIN
        titles t ON s.emp_no = t.emp_no
        AND s.from_date BETWEEN t.from_date AND t.to_date
    GROUP BY
        salary_year,
        t.title
    ORDER BY
        salary_year,
        t.title;
    """
    df2 = pd.read_sql(query2, engine)
    sns.lineplot(ax=axes, x='salary_year', y='avg_salary', hue='title', data=df2, marker='o', errorbar=None)
    axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.setp(axes.get_xticklabels(), rotation=0, ha="right")
    axes.set_title('Average Salary by Job Title Over Time', fontsize=22, fontweight='bold')
    axes.set_xlabel('Year', fontsize=12)
    axes.set_ylabel('Average Salary ($)', fontsize=12)
    axes.ticklabel_format(style='plain', axis='y')
    axes.legend(title='Job Title')

    # --- Final Touches ---
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # --- End of your plotting logic ---
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    # 方式2：返回图片流（可直接作为 <img src="接口地址"> 使用）
    return StreamingResponse(img_buffer, media_type="image/png")
