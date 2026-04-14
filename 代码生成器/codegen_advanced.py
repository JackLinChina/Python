#!/usr/bin/env python3
"""
改进的代码生成器 - 支持从配置文件读取实体定义

使用方法：
    python codegen_advanced.py --entity post           # 使用内置配置
    python codegen_advanced.py --config entities_config.py --entity post  # 使用配置文件
    python codegen_advanced.py --list                  # 列出所有实体
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Optional

# 导入基础生成器
try:
    from codegen import CodeGenerator, EntityConfig, FieldConfig
except ImportError:
    print("错误：无法导入 codegen 模块，请确保 codegen.py 在同一目录")
    sys.exit(1)


class AdvancedCodeGenerator:
    """高级代码生成器（支持配置文件）"""
    
    def __init__(self, config_module=None):
        self.generator = CodeGenerator()
        self.config_module = config_module
        self.entities = self._load_entities()
    
    def _load_entities(self) -> Dict[str, EntityConfig]:
        """从配置模块加载实体"""
        if self.config_module is None:
            return {}
        
        entities = {}
        if hasattr(self.config_module, 'ENTITIES'):
            entities = self.config_module.ENTITIES
        
        return entities
    
    def generate(self, entity_name: str, output_dir: str = "Api") -> bool:
        """生成指定实体的代码"""
        # 首先从配置中查找
        if entity_name in self.entities:
            config = self.entities[entity_name]
            self.generator.save_files(config, output_dir)
            return True
        
        # 否则提示用户
        print(f"❌ 找不到实体: {entity_name}")
        print(f"✓ 已定义的实体: {', '.join(self.entities.keys())}")
        return False
    
    def list_entities(self):
        """列出所有已定义的实体"""
        if not self.entities:
            print("❌ 没有定义任何实体")
            return
        
        print("\n已定义的实体：")
        print("="*60)
        for entity_name, config in self.entities.items():
            print(f"\n  📦 {entity_name}")
            print(f"     中文名: {config.display_name}")
            print(f"     字段数: {len(config.fields)}")
            print(f"     需要认证: {'是' if config.has_auth else '否'}")
            print(f"     字段列表:")
            for field in config.fields:
                print(f"       - {field.name} ({field.type_hint}): {field.description}")
    
    def generate_batch(self, entity_names: list, output_dir: str = "Api"):
        """批量生成多个实体"""
        print(f"\n开始批量生成 {len(entity_names)} 个实体...\n")
        success_count = 0
        for entity_name in entity_names:
            if self.generate(entity_name, output_dir):
                success_count += 1
        
        print(f"\n✓ 生成完成: {success_count}/{len(entity_names)}")
    
    def generate_all(self, output_dir: str = "Api"):
        """生成所有实体"""
        entity_names = list(self.entities.keys())
        self.generate_batch(entity_names, output_dir)


def load_config_module(config_file: str):
    """动态加载配置文件"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return None
    
    if not config_path.name.endswith('.py'):
        print(f"❌ 配置文件必须是 Python 文件: {config_file}")
        return None
    
    # 将 config 文件所在目录添加到 sys.path
    config_dir = str(config_path.parent.absolute())
    if config_dir not in sys.path:
        sys.path.insert(0, config_dir)
    
    # 动态导入模块
    module_name = config_path.stem
    try:
        import importlib
        config_module = importlib.import_module(module_name)
        return config_module
    except ImportError as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="高级代码生成器 - 支持从配置文件读取实体定义",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 列出所有实体
  python codegen_advanced.py --list
  
  # 生成单个实体
  python codegen_advanced.py --entity post
  python codegen_advanced.py --entity product --output ./Api
  
  # 批量生成
  python codegen_advanced.py --batch post product comment
  
  # 生成全部实体
  python codegen_advanced.py --all
  
  # 使用自定义配置文件
  python codegen_advanced.py --config my_entities.py --entity post
  python codegen_advanced.py --config my_entities.py --all
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有已定义的实体"
    )
    parser.add_argument(
        "--entity",
        help="要生成的实体名称"
    )
    parser.add_argument(
        "--batch",
        nargs="+",
        help="批量生成多个实体"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="生成所有已定义的实体"
    )
    parser.add_argument(
        "--config",
        default="entities_config.py",
        help="配置文件路径（默认: entities_config.py）"
    )
    parser.add_argument(
        "--output",
        default="Api",
        help="输出目录（默认: Api）"
    )
    
    args = parser.parse_args()
    
    # 加载配置文件
    config_module = load_config_module(args.config)
    if config_module is None:
        print(f"\n💡 提示：创建 {args.config} 文件来定义实体")
        print("   可参考示例: python example_usage.py")
        return
    
    generator = AdvancedCodeGenerator(config_module)
    
    # 执行命令
    if args.list:
        generator.list_entities()
    elif args.entity:
        generator.generate(args.entity, args.output)
    elif args.batch:
        generator.generate_batch(args.batch, args.output)
    elif args.all:
        generator.generate_all(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
