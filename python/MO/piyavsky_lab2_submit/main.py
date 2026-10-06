import argparse
import ast
import math
import time
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
ALLOWED_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "abs": abs,
}
ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}
ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.UAdd,
    ast.USub,
)
def parse_function(expression):
    """Преобразует строку с функцией в функцию Python."""
    tree = ast.parse(expression, mode="eval")
    allowed_names = {"x", *ALLOWED_FUNCTIONS, *ALLOWED_CONSTANTS}
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Недопустимая конструкция: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise ValueError(f"Недопустимое имя: {node.id}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCTIONS:
                raise ValueError("Недопустимый вызов функции")
    compiled = compile(tree, "<function>", "eval")
    environment = {
        "__builtins__": {},
        **ALLOWED_FUNCTIONS,
        **ALLOWED_CONSTANTS,
    }
    def function(x):
        value = eval(compiled, environment, {"x": float(x)})
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"Функция вернула некорректное значение при x = {x}")
        return value
    return function
def build_vertices(points, L):
    """
    Строит вершины ломаной Пиявского.
    points содержит пары (x, f(x)), отсортированные по x.
    Для каждой пары соседних точек вычисляется пересечение
    двух вспомогательных прямых с наклонами -L и +L.
    """
    vertices = []
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        # Координата пересечения вспомогательных прямых
        x = (x1 + x2) / 2 + (y1 - y2) / (2 * L)
        # Значение нижней оценки в этой точке
        lower_bound = (y1 + y2) / 2 - L * (x2 - x1) / 2
        if not x1 - 1e-12 <= x <= x2 + 1e-12:
            raise ValueError(
                "Константа L слишком мала: "
                "пересечение вспомогательных прямых вышло за интервал"
            )
        vertices.append((x, lower_bound))
    return vertices
def piyavsky(function, a, b, eps, L, max_iterations=100000):
    """Поиск глобального минимума методом ломаных Пиявского."""
    if a >= b:
        raise ValueError("Должно выполняться a < b")
    if eps <= 0:
        raise ValueError("eps должна быть больше нуля")
    if L <= 0:
        raise ValueError("L должна быть больше нуля")
    start_time = time.perf_counter()
    # Начинаем с концов отрезка
    points = [
        (a, function(a)),
        (b, function(b)),
    ]
    iterations = 0
    while iterations < max_iterations:
        points.sort(key=lambda point: point[0])
        vertices = build_vertices(points, L)
        # Самая низкая вершина текущей ломаной
        x_new, lower_bound = min(
            vertices,
            key=lambda vertex: vertex[1],
        )
        # Лучшее уже найденное значение функции
        x_best, f_best = min(
            points,
            key=lambda point: point[1],
        )
        gap = f_best - lower_bound
        # lower_bound <= f* <= f_best
        # Поэтому gap ограничивает ошибку по значению функции.
        if gap <= eps:
            elapsed = time.perf_counter() - start_time
            return {
                "x_min": x_best,
                "f_min": f_best,
                "iterations": iterations,
                "elapsed": elapsed,
                "lower_bound": lower_bound,
                "gap": gap,
                "points": points,
            }
        # Вычисляем функцию в новой точке
        y_new = function(x_new)
        points.append((x_new, y_new))
        iterations += 1
    raise RuntimeError("Достигнуто максимальное число итераций")
def lower_envelope(x_values, points, L):
    """Вычисляет нижнюю ломаную для построения графика."""
    lines = []
    for x, y in points:
        lines.append(y - L * np.abs(x_values - x))
    return np.max(np.vstack(lines), axis=0)
def save_plots(function, result, a, b, L, output_directory="plots"):
    """Строит и сохраняет графики."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    # Эта сетка используется только для отрисовки.
    x_values = np.linspace(a, b, 4000)
    y_values = np.array([function(x) for x in x_values])
    x_min = result["x_min"]
    f_min = result["f_min"]
    # График исходной функции
    plt.figure(figsize=(11, 6))
    plt.plot(x_values, y_values, label="f(x)")
    plt.scatter(
        [x_min],
        [f_min],
        s=70,
        label=f"Минимум ({x_min:.5f}, {f_min:.5f})",
    )
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.title("Функция и найденный глобальный минимум")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        output_directory / "function_and_minimum.png",
        dpi=180,
    )
    plt.close()
    # График функции и нижней ломаной
    envelope = lower_envelope(
        x_values,
        result["points"],
        L,
    )
    point_x = [point[0] for point in result["points"]]
    point_y = [point[1] for point in result["points"]]
    plt.figure(figsize=(11, 6))
    plt.plot(x_values, y_values, label="f(x)")
    plt.plot(
        x_values,
        envelope,
        label="Нижняя ломаная Пиявского",
    )
    plt.scatter(
        point_x,
        point_y,
        s=12,
        label="Вычисленные точки",
    )
    plt.scatter(
        [x_min],
        [f_min],
        s=70,
        label="Найденный минимум",
    )
    plt.axhline(
        result["lower_bound"],
        linestyle="--",
        label=f"Нижняя оценка {result['lower_bound']:.5f}",
    )
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Итоговая ломаная Пиявского")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        output_directory / "piyavsky_broken_line.png",
        dpi=180,
    )
    plt.close()
def main():
    parser = argparse.ArgumentParser(
        description="Метод ломаных Пиявского"
    )
    parser.add_argument("--function", "-f")
    parser.add_argument("--a", type=float)
    parser.add_argument("--b", type=float)
    parser.add_argument("--eps", type=float)
    parser.add_argument("--L", type=float)
    parser.add_argument("--max-iterations", type=int, default=100000)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        # Тестовый пример: одномерная функция Растригина
        expression = "x**2 - 10*cos(2*pi*x) + 10"
        a = -5.12
        b = 5.12
        eps = 0.01
        # f'(x) = 2x + 20*pi*sin(2*pi*x)
        # Поэтому |f'(x)| <= 2*5.12 + 20*pi
        L = 2 * 5.12 + 20 * math.pi
    else:
        if None in (
            args.function,
            args.a,
            args.b,
            args.eps,
            args.L,
        ):
            parser.error(
                "Необходимо задать --function, --a, --b, --eps и --L"
            )
        expression = args.function
        a = args.a
        b = args.b
        eps = args.eps
        L = args.L
    function = parse_function(expression)
    result = piyavsky(
        function,
        a,
        b,
        eps,
        L,
        args.max_iterations,
    )
    save_plots(
        function,
        result,
        a,
        b,
        L,
    )
    print(f"Функция: {expression}")
    print(f"Отрезок: [{a}, {b}]")
    print(f"eps = {eps}")
    print(f"L = {L:.12f}")
    print()
    print(f"x_min ≈ {result['x_min']:.12f}")
    print(f"f(x_min) ≈ {result['f_min']:.12f}")
    print(f"Нижняя оценка ≈ {result['lower_bound']:.12f}")
    print(f"Разрыв ≈ {result['gap']:.12f}")
    print()
    print(f"Итераций: {result['iterations']}")
    print(f"Вычислений функции: {len(result['points'])}")
    print(f"Время: {result['elapsed']:.6f} с")
if __name__ == "__main__":
    main()