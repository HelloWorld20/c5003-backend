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

@router.get('/chart_1', tags=['Visualizations'])
async def get_dashboard_stream():
    """
    Generate the dashboard of Current Employees per Department.
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

    fig, axes = plt.subplots(1, 1, figsize=(22, 18))

    # --- Plot: Number of employees in each department ---
    query1 = """
    SELECT
        d.dept_name,
        COUNT(de.emp_no) AS num_employees
    FROM
        dept_emp de
    JOIN
        departments d ON de.dept_no = d.dept_no
    WHERE
        de.to_date = '9999-01-01'
    GROUP BY
        d.dept_name
    ORDER BY
        num_employees DESC;
    """
    df1 = pd.read_sql(query1, engine)
    sns.barplot(ax=axes, x='num_employees', y='dept_name', data=df1, palette='viridis', orient='h', hue='dept_name', legend=False)
    axes.set_title('Current Employees per Department', fontsize=22, fontweight='bold')
    axes.set_xlabel('Number of Employees', fontsize=12)
    axes.set_ylabel('Department', fontsize=12)

    for p in axes.patches:
        width = p.get_width()
        axes.annotate(
            f'{width:.0f}',  # The text to display
            (width, p.get_y() + p.get_height() / 2.),  # The (x, y) position
            ha='left',          # Horizontal alignment
            va='center',        # Vertical alignment
            xytext=(5, 0),      # 5-point horizontal offset
            textcoords='offset points'
        )

    # --- Final Touches ---
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # --- End of your plotting logic ---
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    # 方式2：返回图片流（可直接作为 <img src="接口地址"> 使用）
    return StreamingResponse(img_buffer, media_type="image/png")
