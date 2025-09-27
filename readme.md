
# 安装与运行

## 前置要求
- Python 3.10+
- MySQL 8+ 已安装并可连接

## 1) 创建并激活虚拟环境
- 方式 A：venv（推荐）
  - macOS/Linux
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
  - Windows（PowerShell）
  ```powershell
  py -3 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- 方式 B：Anaconda/Miniconda（可选）
  ```bash
  conda create -n cityu python=3.10 -y
  conda activate cityu
  ```

## 2) 安装依赖
```bash
pip install -r requirements.txt
```

## 3) 初始化数据库（在 MySQL 客户端执行）
```sql
CREATE DATABASE IF NOT EXISTS cityu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 4) 启动服务
```bash
uvicorn main:app --reload
```

## 5) 访问
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs

# 项目架构
- main.py：应用入口，注册路由与中间件，定义启动/关闭事件与根健康检查
- app/router/：接口层（HTTP API）
  - employee.py：示例接口（部门相关）
  - executor.py：SQL 执行接口（调用数据库层）
- app/db/：数据访问层（数据库连接与 SQL 执行）
  - init.py：数据库连接配置与引擎
  - employee.py：示例查询/返回
  - executor.py：执行传入 SQL，查询返回数据，写入返回受影响行数
- models.py / crud.py / database.py：基于 ORM 的示例与工具（可选，当前路由未直接使用）
- requirements.txt：依赖清单
- readme.md：使用说明

请求流程（简图）
Client → app/router → app/db → MySQL → app/router → Client（在线文档）

### 代码组织

一般情况下，会根据需求来给组织代码，router和db都新建一个对应文件夹，仅处理当前模块的业务逻辑。

比如router和db下都有一个executor.py文件，这里专门处理雇员的信息。如果想要专门处理部门的业务逻辑，请新建一个department.py来写代码，不要混在一起。

### app/router 接口层

接口层是把代码逻辑包装成接口的层。一般情况下，只需要添加一层包装，考虑需要接收的参数，并且调用数据访问层的方法即可。

### app/db 数据访问层

数据访问。主要逻辑写在这里。接收接口层传递来的参数。拼接sql来操作数据库，获得数据库的反馈并且组合数据返回给前端。

