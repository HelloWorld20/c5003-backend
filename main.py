from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
import logging

# 导入自定义模块
# from database import get_db, create_tables, engine

from app.router import employee, title_router, executor, example, employee_view_router, home_viz_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="CityU Backend API",
    description="基于FastAPI和MySQL的后端框架",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# 配置CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee.router)
app.include_router(title_router.router)
app.include_router(employee_view_router.router)
app.include_router(home_viz_router.router)
app.include_router(executor.router)
app.include_router(example.router)


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的操作
    创建数据库表
    """
    logger.info("应用启动中...")
    try:
        # create_tables()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时执行的操作
    """
    logger.info("应用正在关闭...")
    engine.dispose()
    logger.info("数据库连接已关闭")

# 根路径 - 健康检查
@app.get("/", tags=["健康检查"])
async def root():
    """
    根路径接口，用于健康检查
    
    Returns:
        dict: 包含应用信息的字典
    """
    return {
        "message": "CityU Backend API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }



# 如果直接运行此文件，启动开发服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )
