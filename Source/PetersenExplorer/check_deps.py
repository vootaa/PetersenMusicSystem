"""依赖检查工具"""
import sys
from pathlib import Path

def check_dependencies():
    """检查系统依赖"""
    print("🔍 检查PetersenExplorer依赖...")
    
    # 检查PetersenScale_Phi
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from PetersenScale_Phi import PetersenScale_Phi, PHI_PRESETS, DELTA_THETA_PRESETS
        print("✅ PetersenScale_Phi 可用")
        print(f"   φ预设: {len(PHI_PRESETS)}个")
        print(f"   δθ预设: {len(DELTA_THETA_PRESETS)}个")
    except ImportError as e:
        print(f"❌ PetersenScale_Phi 导入失败: {e}")
        return False
    
    # 检查核心模块
    modules_to_check = [
        "core.parameter_explorer",
        "core.evaluation_framework", 
        "core.classification_system",
        "reporting.report_generator"
    ]
    
    available_modules = []
    for module in modules_to_check:
        try:
            __import__(module)
            available_modules.append(module)
            print(f"✅ {module} 可用")
        except ImportError as e:
            print(f"⚠️ {module} 不可用: {e}")
    
    print(f"\n📊 可用模块: {len(available_modules)}/{len(modules_to_check)}")
    return len(available_modules) >= 2  # 至少需要2个核心模块

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)