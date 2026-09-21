from fractions import Fraction

C = [2, 3, 1, 4]       
DIRECTION = "max"      
CONSTRAINTS = [
    ([1, 1, 1, 1], "<=", 10),
    ([2, 1, -1, 1], "=", 8),
    ([0, 1, 2, 1], ">=", 5),
]

def fmt(value):
    return str(value)


def show(table, basis, title):
    print("\n" + title)
    columns = [j for j in range(len(table[0]) - 1) if j not in basis]
    print("Базис |", " | ".join(f"x{j+1}" for j in columns), "| b")
    for i, basic in enumerate(basis):
        print(f"x{basic+1} |", " | ".join(fmt(table[i][j]) for j in columns),
              "|", fmt(table[i][-1]))
    print("p |", " | ".join(fmt(table[-1][j]) for j in columns),
          "| -Q =", fmt(table[-1][-1]))


def set_objective(table, basis, costs):
    "Строим нижнюю строку с оценками и числом -Q."
    bottom = costs[:] + [0]
    for i, basic in enumerate(basis):
        bottom = [bottom[j] - costs[basic] * table[i][j]
                  for j in range(len(bottom))]
    table[-1] = bottom


def pivot(table, basis, row, col):
    "Пересчёт таблицы по разрешающему элементу."
    a = table[row][col]
    table[row] = [x / a for x in table[row]]
    for i in range(len(table)):
        if i != row:
            k = table[i][col]
            table[i] = [table[i][j] - k * table[row][j]
                        for j in range(len(table[i]))]
    basis[row] = col


def simplex(table, basis, phase):
    show(table, basis, f"Фаза {phase}: начальная таблица")
    for step in range(1000):
        negative = [j for j in range(len(table[0]) - 1)
                    if j not in basis and table[-1][j] < 0]
        if not negative:
            return "найден оптимум"
        col = min(negative, key=lambda j: table[-1][j])

        ratios = [(table[i][-1] / table[i][col], i)
                  for i in range(len(basis)) if table[i][col] > 0]
        if not ratios:
            return "целевая функция неограниченна"
        _, row = min(ratios)
        old = basis[row]
        pivot(table, basis, row, col)
        show(table, basis,
             f"Фаза {phase}, шаг {step+1}: x{col+1} входит, x{old+1} выходит")
    raise RuntimeError("Слишком много шагов симплекс-метода")


def solve(c, direction, constraints):
    n = len(c)
    cost = [Fraction(str(x)) * (-1 if direction == "max" else 1) for x in c]
    A, b, signs = [], [], []

    for coefficients, sign, rhs in constraints:
        row = [Fraction(str(x)) for x in coefficients]
        rhs = Fraction(str(rhs))
        if rhs < 0:
            row = [-x for x in row]
            rhs = -rhs
            sign = {"<=": ">=", ">=": "<=", "=": "="}[sign]
        A.append(row)
        b.append(rhs)
        signs.append(sign)

    for i, sign in enumerate(signs):
        if sign != "=":
            for row in A:
                row.append(0)
            A[i][-1] = 1 if sign == "<=" else -1
            cost.append(0)
    real_count = len(cost)

    print("Канонический вид: W -> min, все x >= 0")
    print("Коэффициенты W:", [fmt(x) for x in cost])
    for row, rhs in zip(A, b):
        print([fmt(x) for x in row], "=", fmt(rhs))

    basis = []
    for i in range(len(A)):
        for row in A:
            row.append(0)
        A[i][-1] = 1
        basis.append(real_count + i)
    print("Искусственные переменные:",
          [f"x{j+1}" for j in basis])

    table = [row + [rhs] for row, rhs in zip(A, b)]
    table.append([0] * (len(A[0]) + 1))
    phase_cost = [0] * real_count + [1] * len(A)
    set_objective(table, basis, phase_cost)
    simplex(table, basis, 1)
    if -table[-1][-1] > 0:
        print("Нет допустимых решений: ограничения несовместны")
        return "нет допустимых решений"

    for i in range(len(basis) - 1, -1, -1):
        if basis[i] >= real_count:
            col = next((j for j in range(real_count)
                        if j not in basis and table[i][j] != 0), None)
            if col is None:  
                table.pop(i)
                basis.pop(i)
            else:
                pivot(table, basis, i, col)
    table = [row[:real_count] + [row[-1]] for row in table]

    set_objective(table, basis, cost)
    if simplex(table, basis, 2) == "целевая функция неограниченна":
        print("Нет конечного оптимума: целевая функция неограниченна")
        return "целевая функция неограниченна"

    x = [0] * real_count
    for i, basic in enumerate(basis):
        x[basic] = table[i][-1]
    w = -table[-1][-1]
    z = -w if direction == "max" else w
    print("\nОптимальная точка:", [fmt(value) for value in x[:n]])
    print("Все x канонического вида:", [fmt(value) for value in x])
    print("Значение целевой функции:", fmt(z))
    return "найден оптимум"


if __name__ == "__main__":
    solve(C, DIRECTION, CONSTRAINTS)
