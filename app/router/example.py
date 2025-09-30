from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.db.example import db_get_emp_list
import matplotlib.pyplot as plt
import io
import base64

router = APIRouter()

# 较简单的写法。下方的注释是更复杂的写法，可以提供更多的能力。
# 第一行定义接口。把下方的方法包装成接口提供给前端调用。
# get的第一个参数是接口地址。如下面的例子。启动服务后调用 http://localhost:8000/employees/list 即可调用该接口（调用get_employees_list方法）
# tags是接口分类名称。自定义一个即可
# get_employees_list方法接收的参数就是前端要传递的参数
@router.get('/example/list', tags=['example'])
async def get_employees_list(pageNo, pageSize, emp_no, birth_date, hire_date, name, gender):
    return db_get_emp_list(pageNo, pageSize, emp_no, birth_date, hire_date, name, gender)

@router.get('/example/pic', tags=['example'])
async def get_chart_image():
    """
    生成图表并返回图片数据给前端，不启动 GUI 进程。
    返回 base64 编码的图片数据，前端可直接显示。
    """
    # 使用 Agg 后端，避免启动 GUI
    plt.switch_backend('Agg')
    
    # 创建图表
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.ylabel('some numbers')
    plt.xlabel('x axis')
    plt.title('Sample Chart')
    
    # 将图表保存到内存缓冲区
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    
    # 清理图表，释放内存
    plt.close()
    
    # 方式1：返回 base64 编码的图片数据（JSON 格式）
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return {"image": f"data:image/png;base64,{img_base64}"}

@router.get('/example/pic/stream', tags=['example'])
async def get_chart_stream():
    """
    生成图表并以流的形式返回图片，前端可直接作为图片 URL 使用。
    """
    plt.switch_backend('Agg')
    
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
    plt.ylabel('some numbers')
    plt.xlabel('x axis')
    plt.title('Sample Chart Stream')
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    # 方式2：返回图片流（可直接作为 <img src="接口地址"> 使用）
    return StreamingResponse(img_buffer, media_type="image/png")

# 以下复杂的写法可以提供参数约束、注释功能。
# @router.get('/employees/list', tags=['employees'])
# async def get_employees_list(
#     pageNo: int = Query(..., description="页码，必填"),
#     pageSize: int = Query(..., description="每页条数，必填"),
#     emp_no: int | None = Query(None, description="员工编号，非必填"),
#     birth_date: str | None = Query(None, description="出生日期，非必填"),
#     hire_date: str | None = Query(None, description="入职日期，非必填"),
#     name: str | None = Query(None, description="姓名，非必填"),
#     gender: str | None = Query(None, description="性别，非必填"),
# ):
#     """
#     获取员工列表：将入参原样透传给数据库查询函数。
#     - 必填：pageNo, pageSize
#     - 非必填：emp_no, birth_date, hire_date, name, gender
#     """
#     return db_get_emp_list(**locals())