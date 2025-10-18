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

@router.get('/home_vizs', tags=['Visualizations'])
async def get_dashboard_stream():
    """
    Generate the full 2x2 employee dashboard.
    """
    # Switch backend to 'Agg' for non-GUI server environments
    plt.switch_backend('Agg')

    # --- FIX 1: Corrected database connection check ---
    # We test the connection. If it fails, we return an error immediately.
    # The 'engine' object itself (imported) is assumed to be valid.
    try:
        with engine.connect() as conn:
            print("Database connection successful for dashboard.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        # Return the error directly
        return {"error": f"Database connection error: {e}"}
    
    # If we're here, the connection worked and we can proceed.

    # 1. Create a 2x2 subplot layout
    # We capture the fig object to close it explicitly
    fig, axes = plt.subplots(2, 2, figsize=(22, 18))
    fig.suptitle('Employee Data Analysis Dashboard', fontsize=24, fontweight='bold')

    # --- Plot 1: Number of employees in each department ---
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
    sns.barplot(ax=axes[0, 0], x='num_employees', y='dept_name', data=df1, palette='viridis', orient='h', hue='dept_name', legend=False)
    axes[0, 0].set_title('Current Employees per Department', fontsize=16, fontweight='bold')
    axes[0, 0].set_xlabel('Number of Employees', fontsize=12)
    axes[0, 0].set_ylabel('Department', fontsize=12)

    # --- Plot 2: Average salary over time BY JOB TITLE ---
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
    sns.lineplot(ax=axes[0, 1], x='salary_year', y='avg_salary', hue='title', data=df2, marker='o', errorbar=None)
    axes[0, 1].xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.setp(axes[0, 1].get_xticklabels(), rotation=0, ha="right")
    axes[0, 1].set_title('Average Salary by Job Title Over Time', fontsize=16, fontweight='bold')
    axes[0, 1].set_xlabel('Year', fontsize=12)
    axes[0, 1].set_ylabel('Average Salary ($)', fontsize=12)
    axes[0, 1].ticklabel_format(style='plain', axis='y')
    axes[0, 1].legend(title='Job Title')

    # --- Plot 3: Gender diversity in roles ---
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
    sns.barplot(ax=axes[1, 0], x='title', y='num_employees', hue='gender', data=df3, palette='muted')
    axes[1, 0].set_title('Gender Diversity in Current Roles', fontsize=16, fontweight='bold')
    axes[1, 0].set_xlabel('Job Title', fontsize=12)
    axes[1, 0].set_ylabel('Number of Employees', fontsize=12)
    axes[1, 0].tick_params(axis='x', rotation=45)

    # --- Plot 4: Employee tenure distribution per department ---
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

    sns.boxplot(ax=axes[1, 1], x='tenure', y='dept_name', data=df4, palette='plasma', orient='h', order=order, hue='dept_name', legend=False)
    axes[1, 1].set_title('Tenure Distribution of Current Employees', fontsize=16, fontweight='bold')
    axes[1, 1].set_xlabel('Tenure in Department (Years)', fontsize=12)
    axes[1, 1].set_ylabel('Department', fontsize=12)

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
            axes[1, 1].text(x=value, y=y - 0.3, s=f'{value:.1f}', ha='center',
                            va='center', fontweight='bold', color='white', fontsize=10,
                            bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.6))

    # --- Final Touches ---
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # --- End of your plotting logic ---
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    # 方式2：返回图片流（可直接作为 <img src="接口地址"> 使用）
    return StreamingResponse(img_buffer, media_type="image/png")