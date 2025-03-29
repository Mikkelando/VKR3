import numpy as np
import pandas as pd
import pprint
import inspect
import ast

def get_variable_name(obj):
    """Возвращает имя переменной из вызова функции (best effort, не всегда работает)"""
    frame = inspect.currentframe()
    try:
        outer_frame = frame.f_back.f_back  # два уровня назад: get_variable_name -> vprint -> внешка
        code = inspect.getframeinfo(outer_frame).code_context[0]
        parsed = ast.parse(code)
        call = parsed.body[0].value  # ожидаем: vprint(...)
        if isinstance(call, ast.Call):
            arg = call.args[0]
            if isinstance(arg, ast.Name):
                return arg.id
            elif isinstance(arg, ast.Attribute):
                return f"{arg.value.id}.{arg.attr}"
            elif isinstance(arg, ast.Subscript):
                return ast.unparse(arg)
        return "<?>"
    except Exception:
        return "<?>"
    finally:
        del frame

def vprint(obj, max_rows=10, max_cols=10, floatfmt="{:.3f}"):
    name = get_variable_name(obj)
    print("\n" + "="*80)
    print(f"🔍 Variable: `{name}` — Type: {type(obj).__name__}")
    print("="*80)

    if isinstance(obj, pd.DataFrame):
        pd.set_option('display.max_rows', max_rows)
        pd.set_option('display.max_columns', max_cols)
        pd.set_option('display.width', 120)
        pd.set_option('display.float_format', lambda x: floatfmt.format(x))
        print(obj)
    elif isinstance(obj, pd.Series):
        pd.set_option('display.max_rows', max_rows)
        pd.set_option('display.float_format', lambda x: floatfmt.format(x))
        print(obj)
    elif isinstance(obj, np.ndarray):
        if obj.ndim == 1:
            print("🔢 Numpy array (1D):")
            print(np.array2string(obj, precision=3, threshold=max_rows))
        else:
            print(f"🔢 Numpy array {obj.shape}:")
            print(np.array2string(obj, precision=3, threshold=max_rows*max_cols))
    elif isinstance(obj, (list, dict, tuple)):
        pprint.pprint(obj, width=120)
    else:
        print(obj)
    print("="*80 + "\n")