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

@router.get('/chart_3', tags=['Visualizations'])
async def get_dashboard_stream():
    """
    Generate the dashboard of Gender Diversity in Current Roles.
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

    # --- Plot: Gender diversity in roles ---
    query3 = """
    SELECT
        t.title,
        e.gender,
        COUNT(e.emp_no) AS num_employees
    FROM
        employees e
    JOIN
        titles t ON e.emp_no = t.emp_no
    WHERE
        t.to_date = '9999-01-01'
    GROUP BY
        t.title,
        e.gender
    ORDER BY
        num_employees DESC;
    """
    df3 = pd.read_sql(query3, engine)
    sns.barplot(ax=axes, x='title', y='num_employees', hue='gender', data=df3, palette='muted')
    axes.set_title('Gender Diversity in Current Roles', fontsize=22, fontweight='bold')
    axes.set_xlabel('Job Title', fontsize=12)
    axes.set_ylabel('Number of Employees', fontsize=12)
    axes.tick_params(axis='x', rotation=0)

    for p in axes.patches:
        height = p.get_height()
        if height > 0:  # Only add labels to bars with a value
            axes.annotate(
                f'{height:.0f}',  # The text to display (as an integer)
                (p.get_x() + p.get_width() / 2., height),  # The (x, y) position
                ha='center',         # Horizontal alignment
                va='bottom',         # Vertical alignment
                xytext=(0, 5),       # 5-point vertical offset
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
