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

@router.get('/chart_4', tags=['Visualizations'])
async def get_dashboard_stream():
    """
    Generate the dashboard of Tenure Distribution of Current Employees.
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

    # --- Plot: Employee tenure distribution per department ---
    query4 = """
    SELECT
        d.dept_name,
        DATEDIFF(
            IF(de.to_date = '9999-01-01',
            (SELECT MAX(to_date)
                FROM dept_emp
                WHERE to_date != '9999-01-01'),
            de.to_date),
            de.from_date
        ) / 365.25 AS tenure
    FROM
        dept_emp de
    JOIN
        departments d ON de.dept_no = d.dept_no;
    """
    df4 = pd.read_sql(query4, engine)
    
    stats_df = df4.groupby('dept_name')['tenure'].describe()
    order = stats_df['50%'].sort_values(ascending=False).index

    sns.boxplot(ax=axes, x='tenure', y='dept_name', data=df4, palette='plasma', orient='h', order=order, hue='dept_name', legend=False)
    axes.set_title('Tenure Distribution of Current Employees', fontsize=22, fontweight='bold')
    axes.set_xlabel('Tenure in Department (Years)', fontsize=12)
    axes.set_ylabel('Department', fontsize=12)

    y_positions = {dept: i for i, dept in enumerate(order)}

    for dept in order:
        stats = {
            'Min': stats_df.loc[dept, 'min'],
            'Q1': stats_df.loc[dept, '25%'],
            'Median': stats_df.loc[dept, '50%'],
            'Q3': stats_df.loc[dept, '75%'],
            'Max': stats_df.loc[dept, 'max']
        }
        y = y_positions[dept]
        
        for key, value in stats.items():
            axes.text(x=value, y=y - 0.3, s=f'{value:.1f}', ha='center',
                            va='center', fontweight='bold', color='white', fontsize=10,
                            bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.6))

    # --- Final Touches ---
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # --- End of your plotting logic ---
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    # 方式2：返回图片流（可直接作为 <img src="接口地址"> 使用）
    return StreamingResponse(img_buffer, media_type="image/png")
