"""
app.py - Flask Web 应用

可视化代码生成器 Web 服务
运行方式: python app.py
访问地址: http://127.0.0.1:5000
"""
import os
import json
import traceback
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import zipfile
from io import BytesIO

from db_reader import create_reader, TableInfo
from codegen import CodeGenerator, EntityConfig, FieldConfig
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 存储会话数据
sessions = {}
# 存储生成的压缩文件路径，方便清理
generated_files = {}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """测试数据库连接"""
    try:
        data = request.json
        db_type = data.get('db_type', '').lower()
        
        # 根据数据库类型提取不同的参数
        if db_type == 'mysql':
            params = {
                'host': data.get('host'),
                'port': int(data.get('port', 3306)),
                'user': data.get('user'),
                'password': data.get('password'),
                'database': data.get('database')
            }
        elif db_type == 'postgresql':
            params = {
                'host': data.get('host'),
                'port': int(data.get('port', 5432)),
                'user': data.get('user'),
                'password': data.get('password'),
                'database': data.get('database')
            }
        elif db_type == 'sqlserver':
            params = {
                'server': data.get('server'),
                'database': data.get('database'),
                'user': data.get('user'),
                'password': data.get('password'),
                'port': int(data.get('port', 1433))
            }
        elif db_type == 'oracle':
            params = {
                'host': data.get('host'),
                'port': int(data.get('port', 1521)),
                'user': data.get('user'),
                'password': data.get('password'),
                'service_name': data.get('service_name', 'ORCL')
            }
        else:
            return jsonify({'success': False, 'message': f'不支持的数据库类型: {db_type}'})
        
        reader = create_reader(db_type, **params)
        
        if reader.test_connection():
            # 保存连接信息到会话
            session_id = data.get('session_id', 'default')
            sessions[session_id] = {
                'db_type': db_type,
                'reader': reader,
                'params': params
            }
            return jsonify({'success': True, 'message': '连接成功！'})
        else:
            return jsonify({'success': False, 'message': '连接失败，请检查连接参数'})
    
    except Exception as e:
        logger.error(f"连接测试异常: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'连接失败: {str(e)}'})


@app.route('/api/get-tables', methods=['POST'])
def get_tables():
    """获取数据库表列表"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': '请先创建有效的数据库连接'})
        
        session = sessions[session_id]
        reader = session['reader']
        tables = reader.get_tables()
        
        return jsonify({'success': True, 'tables': tables})
    
    except Exception as e:
        logger.error(f"获取表列表异常: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取表列表失败: {str(e)}'})


@app.route('/api/get-table-info', methods=['POST'])
def get_table_info():
    """获取表详细信息（字段列表）"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        table_name = data.get('table_name')
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': '请先创建有效的数据库连接'})
        
        if not table_name:
            return jsonify({'success': False, 'message': '表名不能为空'})
        
        session = sessions[session_id]
        reader = session['reader']
        table_info = reader.get_table_info(table_name)
        
        # 转换为 JSON 序列化格式
        columns = []
        for col in table_info.columns:
            columns.append({
                'name': col.name,
                'type': col.type,
                'nullable': col.nullable,
                'is_primary_key': col.is_primary_key,
                'comment': col.comment
            })
        
        return jsonify({
            'success': True,
            'table_name': table_info.name,
            'comment': table_info.comment,
            'columns': columns
        })
    
    except Exception as e:
        logger.error(f"获取表信息异常: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'获取表信息失败: {str(e)}'})


@app.route('/api/generate-code', methods=['POST'])
def generate_code():
    """生成代码并压缩为 ZIP 文件"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        table_configs = data.get('tables', [])  # 选中的表配置列表
        
        if session_id not in sessions:
            return jsonify({'success': False, 'message': '数据库连接已过期'})
        
        if not table_configs:
            return jsonify({'success': False, 'message': '请至少选择一个表'})
        
        session = sessions[session_id]
        reader = session['reader']
        
        # 创建临时目录用于生成代码
        temp_dir = tempfile.mkdtemp(prefix='codegen_')
        output_path = os.path.join(temp_dir, 'Api')
        
        try:
            generator = CodeGenerator(output_path)
            generated_files_list = []
            
            # 为每个选中的表生成代码
            for table_config in table_configs:
                table_name = table_config.get('table_name')
                display_name = table_config.get('display_name')
                selected_columns = table_config.get('columns', [])
                
                # 获取表信息
                table_info = reader.get_table_info(table_name)
                
                # 根据选中的列构建字段配置
                fields = []
                for column in table_info.columns:
                    if not column.is_primary_key and column.name in selected_columns:
                        # 将数据库类型转换为 Python 类型提示
                        type_hint = _map_db_type_to_python(column.type)
                        
                        fields.append(FieldConfig(
                            name=column.name,
                            type_hint=type_hint,
                            db_type=column.type,
                            required=not column.nullable,
                            description=column.comment
                        ))
                
                if not fields:
                    continue
                
                # 创建实体配置
                entity_config = EntityConfig(
                    name=table_name,
                    display_name=display_name or table_name,
                    fields=fields,
                    has_auth=True
                )
                
                # 生成文件
                try:
                    generator.save_files(entity_config, output_path)
                    generated_files_list.append(table_name)
                except Exception as e:
                    logger.error(f"生成 {table_name} 失败: {str(e)}")
            
            if not generated_files_list:
                shutil.rmtree(temp_dir)
                return jsonify({'success': False, 'message': '没有成功生成任何代码'})
            
            # 将生成的代码压缩为 ZIP 文件
            zip_filename = f"generated_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            
            # 压缩 Api 目录
            def zipdir(path, ziph):
                """递归压缩目录"""
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        ziph.write(file_path, arcname)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipdir(output_path, zipf)
            
            # 保存生成的文件路径，用于后续下载
            download_key = f"{session_id}_{datetime.now().timestamp()}"
            generated_files[download_key] = {
                'zip_path': zip_path,
                'temp_dir': temp_dir,
                'filename': zip_filename,
                'tables': generated_files_list
            }
            
            # 清理临时生成的代码（保留 zip 文件）
            shutil.rmtree(output_path)
            
            return jsonify({
                'success': True,
                'message': f'成功生成 {len(generated_files_list)} 个模块',
                'generated_files': generated_files_list,
                'download_key': download_key,
                'filename': zip_filename
            })
        
        except Exception as e:
            # 发生错误时清理临时目录
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            logger.error(f"代码生成异常: {traceback.format_exc()}")
            return jsonify({'success': False, 'message': f'代码生成失败: {str(e)}'})
    
    except Exception as e:
        logger.error(f"代码生成异常: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'代码生成失败: {str(e)}'})


@app.route('/api/download-code/<download_key>', methods=['GET'])
def download_code(download_key):
    """下载生成的代码 ZIP 文件"""
    try:
        if download_key not in generated_files:
            return jsonify({'error': '下载链接已过期或无效'}), 404
        
        file_info = generated_files[download_key]
        zip_path = file_info['zip_path']
        filename = file_info['filename']
        
        if not os.path.exists(zip_path):
            del generated_files[download_key]
            return jsonify({'error': '文件不存在'}), 404
        
        # 发送文件
        response = send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
        
        # 文件下载完成后清理临时文件
        @response.call_on_close
        def cleanup():
            try:
                temp_dir = file_info['temp_dir']
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                if download_key in generated_files:
                    del generated_files[download_key]
                logger.info(f"已清理临时文件: {temp_dir}")
            except Exception as e:
                logger.error(f"清理临时文件失败: {str(e)}")
        
        return response
    
    except Exception as e:
        logger.error(f"下载代码异常: {traceback.format_exc()}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


def _map_db_type_to_python(db_type: str) -> str:
    """将数据库字段类型映射到 Python 类型提示"""
    db_type_lower = db_type.lower()
    
    # MySQL/PostgreSQL/SQL Server 类型映射
    if any(x in db_type_lower for x in ['int', 'integer', 'bigint', 'smallint']):
        return 'int'
    elif any(x in db_type_lower for x in ['float', 'double', 'decimal', 'numeric']):
        return 'float'
    elif any(x in db_type_lower for x in ['varchar', 'char', 'text', 'nvarchar', 'nchar']):
        return 'str'
    elif any(x in db_type_lower for x in ['date', 'datetime', 'timestamp']):
        return 'datetime'
    elif any(x in db_type_lower for x in ['bool', 'boolean', 'bit']):
        return 'bool'
    else:
        return 'str'  # 默认为字符串


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({'error': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    logger.error(f"内部错误: {traceback.format_exc()}")
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 创建 templates 文件夹
    os.makedirs('templates', exist_ok=True)
    os.makedirs('Api', exist_ok=True)
    
    print("\n" + "="*60)
    print("可视化代码生成器启动中...")
    print("="*60)
    print("访问地址: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
