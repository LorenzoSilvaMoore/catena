import catena
from decimal import Decimal
if __name__ == "__main__":
    # # Example usage of the catena library
    # md = 1000000
    # cf1 = catena.FiniteSimpleContinuedFraction.from_float(3.245, max_denominator=md)
    # cf2 = catena.FiniteSimpleContinuedFraction.from_float(2.71828, max_denominator=md)

    # print("CF1:", cf1)
    # print("CF2:", cf2)

    # sum_cf = cf1 + cf2
    # print("Sum of CF1 and CF2:", sum_cf)

    # tc = sum_cf.terminal_convergent
    # print("Terminal convergent of the sum:", tc)
    # print("Decimal approximation of the sum:", tc[0] / tc[1])

    # print(catena.mathlib.convert.from_decimal_to_rational("0.92592592592"))

    # print("CF1 limit convergent:", cf1.terminal_convergent)
    # print("CF1 limit convergent as decimal:", Decimal(cf1.terminal_convergent[0]) / Decimal(cf1.terminal_convergent[1]))

    # print("CF2 limit convergent:", cf2.terminal_convergent)
    # print("CF2 limit convergent as decimal:", Decimal(cf2.terminal_convergent[0]) / Decimal(cf2.terminal_convergent[1]))

    # print("Sum of CF1 and CF2 limit convergent:", sum_cf.terminal_convergent)
    # print("Sum of CF1 and CF2 limit convergent as decimal:", Decimal(sum_cf.terminal_convergent[0]) / Decimal(sum_cf.terminal_convergent[1]))

    x = catena.FiniteSimpleContinuedFraction([], integer_part=5)
    print(x.terminal_convergent)