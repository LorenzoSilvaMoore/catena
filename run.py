import catena
from decimal import Decimal, getcontext
from fractions import Fraction

from sympy.ntheory import continued_fraction_periodic, continued_fraction_convergents, continued_fraction_reduce
from math import gcd, isqrt

from random import randint, random, shuffle

def periodic_scf_to_quadratic(cycle: list[int]) -> tuple[int, int, int]:
    """Given the periodic part and optional pre-period of a simple continued fraction, return the coefficients of the corresponding quadratic polynomial."""
    k = len(cycle)
    scf = catena.SimpleContinuedFraction(generator=lambda n: cycle[n % k])
    ck = scf.convergent(k-1)
    ck_minus_1 = scf.convergent(k-2)
    pk, qk = ck
    pk_minus_1, qk_minus_1 = ck_minus_1
    A = qk_minus_1
    B = qk - pk_minus_1
    C = -pk
    return int(A), int(B), int(C)

def periodic_scf_with_int_to_quadratic(cycle: list[int], integer_part: int) -> tuple[int, int, int]:
    """Given the periodic part and pre-period of a simple continued fraction, return the coefficients of the corresponding quadratic polynomial."""
    A, B, C = periodic_scf_to_quadratic(cycle)
    # Adjust coefficients to account for the integer part
    A_new = A
    B_new = B - 2 * A * integer_part
    C_new = C + A * integer_part**2 - B * integer_part
    return int(A_new), int(B_new), int(C_new)

def periodic_scf_with_pad_to_quadratic(cycle: list[int], pad: list[int]) -> tuple[int, int, int]:
    """Given the periodic part and pre-period of a simple continued fraction, return the coefficients of the corresponding quadratic polynomial."""
    scf = catena.FiniteSimpleContinuedFraction(pad)
    ck = scf.convergent(len(pad)-1)
    ck_minus_1 = scf.convergent(len(pad)-2)
    
    pk, qk = ck
    pk_minus_1, qk_minus_1 = ck_minus_1
    A, B, C = periodic_scf_to_quadratic(cycle)

    # Adjust coefficients to account for the pre-period
    A_new = A * qk**2 - B * qk * qk_minus_1 + C * qk_minus_1**2
    B_new = -2 * A * pk * qk + B * (pk * qk_minus_1 + pk_minus_1 * qk) - 2 * C * pk_minus_1 * qk_minus_1
    C_new = A * pk**2 - B * pk * pk_minus_1 + C * pk_minus_1**2
    return int(A_new), int(B_new), int(C_new)


def periodic_scf_with_pad_and_int_to_quadratic(cycle: list[int], pad: list[int], integer_part: int) -> tuple[int, int, int]:
    """Given the periodic part and pre-period of a simple continued fraction, return the coefficients of the corresponding quadratic polynomial."""
    A, B, C = periodic_scf_with_pad_to_quadratic(cycle, pad)
    # Adjust coefficients to account for the integer part
    A_new = A
    B_new = B - 2 * A * integer_part
    C_new = C + A * integer_part**2 - B * integer_part
    return int(A_new), int(B_new), int(C_new)

def _square_part_sqrt(D: int) -> int:
    """Returns the largest integer s such that s² divides D."""
    s, n, p = 1, D, 2
    while p * p <= n:
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        s *= p ** (count // 2)
        p += 1
    return s

def random_fscf() -> catena.FiniteSimpleContinuedFraction:
    """Generates a random finite simple continued fraction."""
    small_lo = randint(1, 3)
    small_coefficients = (randint(1, small_lo) for _ in range(randint(60,80)))
    large_lo = randint(17, 100)
    large_coefficients = ()
    if randint(0, 1) == 0:
        large_coefficients = (randint(1, large_lo) for _ in range(randint(10, 20)))

    int_part = randint(-10, 10)
    #shuffle the coefficients
    coefficients = list(small_coefficients) + list(large_coefficients)
    shuffle(coefficients)
    return catena.FiniteSimpleContinuedFraction(coefficients, integer_part=int_part)


def find_plateau_order(fscf: catena.FiniteSimpleContinuedFraction) -> int:
    """Finds the order of at which the floating-point approximation of the convergents of a finite simple continued fraction stabilizes."""
    prev_approx = None
    for n in range(1, 1000):
        c = fscf.convergent(n)
        approx = float(Decimal(c[0]) / Decimal(c[1]))
        if prev_approx is not None and approx == prev_approx:
            return n
        prev_approx = approx
    return -1  # Return -1 if no plateau is found within the first 1000 convergents


if __name__ == "__main__":
    # sqer(14) = [3; 1, 2, 1, 6, 1, 2, 1, 6, ...]
    # cycle = (1,2,1,6)
    # generator = catena.Generator(generator=lambda n: cycle[n % len(cycle)])
    # scf = catena.SimpleContinuedFraction(generator)

    # y = Decimal(14).sqrt() - 3 
    
    # c100 = scf.convergent(100)
    # y_approx = Decimal(c100[0]) / Decimal(c100[1])
    # print(f"True value of sqrt(14): {Decimal(14).sqrt()}")
    # print(f"100th convergent of sqrt(14): {c100} ≈ {y_approx}")

    # c3 = scf.convergent(3)
    # print(f"4th convergent of sqrt(14): {c3} ≈ {Decimal(c3[0]) / Decimal(c3[1])}")
    # c2 = scf.convergent(2)
    # print(f"3rd convergent of sqrt(14): {c2} ≈ {Decimal(c2[0]) / Decimal(c2[1])}")

    # p3, q3 = map(Decimal, c3)
    # p2, q2 = map(Decimal, c2)

    # print(f"Mapping: ", (p3 + p2 * y) / (q3 + q2 * y))

    # print(f"Mapping 2: ", (p2 + p3 * y) / (q2 + q3 * y))

    # eval1 = q2 * y**2 + (q3 - p2) * y - p3
    # eval2 = q2 * y_approx**2 + (q3 - p2) * y_approx - p3

    # print(f"Evaluating the mapping at sqrt(14): {eval1}")
    # print(f"Evaluating the mapping at the approximation: {eval2}")

    # print(catena.FiniteSimpleContinuedFraction(cycle).terminal_convergent)
    # print(catena.FiniteSimpleContinuedFraction(cycle).convergent(2))

    # pad = [1, 1, 1]
    # cycle = [1, 2, 1, 6]
    # generator = lambda n: pad[n] if n < len(pad) else cycle[(n - len(pad)) % len(cycle)]
    # k = len(pad)
    # m = len(cycle)
    # scf = catena.SimpleContinuedFraction(generator)
    # print(scf.convergent(k-1))
    # print(scf.convergent(k+m-1))

    # print(catena.FiniteSimpleContinuedFraction(pad).terminal_convergent)
    # print(catena.FiniteSimpleContinuedFraction(pad + cycle).terminal_convergent)

    # ck = scf.convergent(k-1)
    # ck_minus_1 = scf.convergent(k-2)
    # ckm = scf.convergent(k+m-1)
    # ckm_minus_1 = scf.convergent(k+m-2)

    # print(f"ck: {ck}, ck-1: {ck_minus_1}, ckm: {ckm}, ckm-1: {ckm_minus_1}")

    # pk, qk = map(Decimal, ck)
    # pk_minus_1, qk_minus_1 = map(Decimal, ck_minus_1)
    # pkm, qkm = map(Decimal, ckm)
    # pkm_minus_1, qkm_minus_1 = map(Decimal, ckm_minus_1)

    # A = pk_minus_1 * qkm_minus_1 - pkm_minus_1 * qkm_minus_1
    # B = pk * qkm_minus_1 + pk_minus_1 * qkm - pkm * qk_minus_1 - pkm_minus_1 * qk
    # C = pk * qkm - pkm * qk

    # c100 = scf.convergent(100)
    # y_approx = Decimal(c100[0]) / Decimal(c100[1])
    # print(f"APPROXIMATION: {y_approx}")
    # eval_at_approx = A * y_approx**2 + B * y_approx + C
    # print(f"Evaluating the polynomial at the approximation: {eval_at_approx}")


    # print(f"Polynomial coefficients: A={A}, B={B}, C={C}")

    # left_side = (pk + pk_minus_1 * y_approx) / (qk + qk_minus_1 * y_approx)
    # right_side = (pkm + pkm_minus_1 * y_approx) / (qkm + qkm_minus_1 * y_approx)
    # print(f"Left side of the mapping at the approximation: {left_side}")
    # print(f"Right side of the mapping at the approximation: {right_side}")

    # left_side2 = (pk + pk_minus_1 * y_approx) * (qkm + qkm_minus_1 * y_approx)
    # right_side2 = (pkm + pkm_minus_1 * y_approx) * (qk + qk_minus_1 * y_approx)
    # print(f"Left side (cross-multiplied) at the approximation: {left_side2}")
    # print(f"Right side (cross-multiplied) at the approximation: {right_side2}")

    # left_side3 = pk * qkm + pk_minus_1 * qkm * y_approx + pk * qkm_minus_1 * y_approx + pk_minus_1 * qkm_minus_1 * y_approx**2
    # right_side3 = pkm * qk + pkm_minus_1 * qk * y_approx + pkm * qk_minus_1 * y_approx + pkm_minus_1 * qk_minus_1 * y_approx**2
    # print(f"Left side (fully expanded) at the approximation: {left_side3}")
    # print(f"Right side (fully expanded) at the approximation: {right_side3}")

    # # pure periodic case
    # generator2 = lambda n: cycle[n % len(cycle)]
    # scf2 = catena.SimpleContinuedFraction(generator2)
    # c2k = scf2.convergent(k-1)
    # c2k_minus_1 = scf2.convergent(k-2)

    # cycle = [5, 1, 1, 1, 24, 1, 1, 1]
    # generator = lambda n: cycle[n % len(cycle)]
    # scf = catena.SimpleContinuedFraction(generator)
    # c100 = scf.convergent(100)
    # y_approx = Decimal(c100[0]) / Decimal(c100[1])
    # print(f"Approximation of the root from the SCF: {y_approx}")
    # A, B, C = periodic_scf_to_quadratic(cycle)
    # print(f"Quadratic coefficients for cycle {cycle}: A={A}, B={B}, C={C}")
    # root1 = (-B + Decimal(B**2 - 4 * A * C).sqrt()) / (2 * A)
    # print(f"Root of the quadratic for cycle {cycle}: {root1}")

    # integer_part = 2
    # scf = scf + integer_part
    # c100 = scf.convergent(100)
    # y_approx = Decimal(c100[0]) / Decimal(c100[1])
    # print(f"Approximation of the root from the SCF with integer part {integer_part}: {y_approx}")
    # A2, B2, C2 = periodic_scf_with_int_to_quadratic(cycle, integer_part)
    # print(f"Quadratic coefficients for cycle {cycle} with integer part {integer_part}: A={A2}, B={B2}, C={C2}")
    # root2 = (-B2 + Decimal(B2**2 - 4 * A2 * C2).sqrt()) / (2 * A2)
    # print(f"Root of the quadratic for cycle {cycle} with integer part {integer_part}: {root2}")

    # print("")
    # pad = [1, 1]
    # generator = lambda n: pad[n] if n < len(pad) else cycle[(n - len(pad)) % len(cycle)]
    # scf = catena.SimpleContinuedFraction(generator)
    # c100 = scf.convergent(100)
    # y_approx = Decimal(c100[0]) / Decimal(c100[1])
    # print(f"Approximation of the root from the SCF with pad: {y_approx}")
    # A3, B3, C3 = map(Decimal, periodic_scf_with_pad_to_quadratic(cycle, pad))
    # print(f"Quadratic coefficients for cycle {cycle} with pad {pad}: A={A3}, B={B3}, C={C3}")

    # root3 = (-B3 + Decimal(B3**2 - 4 * A3 * C3).sqrt()) / (2 * A3)
    # print(f"Root of the quadratic for cycle {cycle} with pad {pad}: {root3}")
    # print(catena.FiniteSimpleContinuedFraction.from_decimal(str(root3)))

    # print("")
    # scf = scf + integer_part
    # c100 = scf.convergent(100)
    # y_approx = Decimal(c100[0]) / Decimal(c100[1])
    # print(f"Approximation of the root from the SCF with pad and integer part: {y_approx}")
    # A4, B4, C4 = map(Decimal, periodic_scf_with_pad_and_int_to_quadratic(cycle, pad, integer_part))
    # print(f"Quadratic coefficients for cycle {cycle} with pad {pad} and integer part {integer_part}: A={A4}, B={B4}, C={C4}")
    # root4 = (-B4 + Decimal(B4**2 - 4 * A4 * C4).sqrt()) / (2 * A4)
    # print(f"Root of the quadratic for cycle {cycle} with pad {pad} and integer part {integer_part}: {root4}")
    # print(catena.FiniteSimpleContinuedFraction.from_decimal(str(root4)))

    # P = Decimal(7)
    # Q = Decimal(10).sqrt()
    # S = Decimal(4)

    # X = (P + Q) / S

    # print(catena.FiniteSimpleContinuedFraction.from_decimal(str(X)))

    # pscf = catena.PeriodicSimpleContinuedFraction(period=cycle, pre_period=pad, integer_part=0)

    # A, B, C = pscf.quadratic_coefficients()
    # print(f"Coefficients from the class method: {(A, B, C)}")
    # print(f"Floating-point approximation from the class method: {float(pscf)}")

    # P = Decimal(-B)
    # D = Decimal(B)**2 - 4*Decimal(A)*Decimal(C)
    # Q = 2*Decimal(A)
    # conjugate = (P - D.sqrt()) / Q
    # print(f"Conjugate root: {conjugate}")
    # print(catena.FiniteSimpleContinuedFraction.from_decimal(str(conjugate)))
    getcontext().prec = 500
    # A = 2
    # B = -5
    # C = -5
    # P = Decimal(-B)
    # Q = Decimal(B)**2 - 4*Decimal(A)*Decimal(C)
    # if Q < 0:
    #     print("The roots are complex, cannot proceed.")
    #     exit(1)
    # S = 2*Decimal(A)
    # X = (P + Q.sqrt()) / S
    # X_conjugate = (P - Q.sqrt()) / S
    # print(f"X: {X}")
    # print(f"Conjugate of X: {X_conjugate}")
    # print(catena.FiniteSimpleContinuedFraction.from_decimal(str(X)))

    # pad = [1]
    # cycle = [3, 1, 3,]
    # pscf = catena.PeriodicSimpleContinuedFraction(period=cycle, pre_period=pad, integer_part=2)#int(X))
    # print(f"PSCF: {pscf}")
    # print(f"PSCF as decimal: {float(pscf)}")
    # print(f"PSCF quadratic coefficients: {pscf.quadratic_coefficients()}")

    # for n in range(20):
    #     c = pscf.generator(n)
    #     print(f"Term {n}: {c}")

    # for P in range(-15, 16):
    #     for Q in range(-15, 16):
    #         if Q == 0:
    #             continue
    #         for D in range(1, 20):
    #             if isqrt(D)**2 == D:
    #                 continue

    #             if Q < 0:
    #                 P = -P
    #                 Q = -Q

    #             X = (Decimal(P) + Decimal(D).sqrt()) / Decimal(Q)
                
    #             # Transform the surd into a quadratic form
    #             P0 = P * 2 * Q
    #             Q0 = Q * 2 * Q
    #             D0 = D * 4 * Q**2
    #             A = Q * Q
    #             B = -P0
    #             C = (P0**2 - D0) // (4 * Q * Q)
    #             g = gcd(A, B, C)
    #             A, B, C = Decimal(A // g), Decimal(B // g), Decimal(C // g)
    #             x0 = (-B + Decimal(B**2 - 4 * A * C).sqrt()) / (2 * A)
    #             x1 = (-B - Decimal(B**2 - 4 * A * C).sqrt()) / (2 * A)

    #             if 6 < x0 and 4 < x1:
    #                 print(f"P={P}, Q={Q}, D={D} => X={float(X)}")
    #                 print(f"Quadratic form: {A}x^2 + {B}x + {C} = 0")
    #                 print(f"Roots: {float(x0)}, {float(x1)}")
    #                 print("Both roots are greater than 1 in absolute value, skipping.")
                    
    #                 scf1 = catena.FiniteSimpleContinuedFraction.from_decimal(str(x0))
    #                 scf2 = catena.FiniteSimpleContinuedFraction.from_decimal(str(x1))
    #                 print(f"SCF of root 1: {scf1}")
    #                 print(f"SCF of root 2: {scf2}")
                    

    # P=8, Q=10, D=3 => X=0.9732050807568877
    # Quadratic form: 100x^2 + -160x + 61 = 0
    # Roots: 0.9732050807568877, 0.6267949192431123
    # Both roots are greater than 1 in absolute value, skipping.
    # SCF of root 1: FiniteSimpleContinuedFraction(partial_quotients=(1, 36, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 9, 1, 27, 1, 1, 1, 1, 1, 3, 3, 2, 7, 1, 1, 7, 1, 34, 1, 2, 2, 1, 4, 2, 1, 2, 2, 6, 1, 21, 1, 1, 1, 2, 2, 1, 13, 2, 1, 2, 1, 1, 3, 1, 1, 1, 1, 2, 9, 1, 1, 1, 1, 2, 5, 1, 9, 1, 2, 10, 1, 1, 1, 4, 6, 1, 132, 1, 2, 1, 1, 2, 1, 1, 1, 15, 1, 3, 1, 1, 2, 16, 3, 10, 2, 30, 1, 3, 1, 25, 2, 1, 9, 2, 3, 2, 6, 1, 2, 2, 1, 1, 1, 42, 1, 1, 1, 1, 7, 403, 1, 1, 3, 6, 1, 6, 1, 1, 9, 1, 29, 1, 4, 1, 18, 1, 2, 14, 2, 1, 18, 3, 1, 27, 3, 9, 3, 4, 1, 2, 5, 3, 2, 4, 1, 1, 1, 1, 1, 1, 3, 4, 2, 2, 2, 2, 1, 5, 2, 1, 12, 2, 1, 2, 4, 1, 105, 1, 2, 3, 1, 52, 23, 2, 1, 1, 3, 3, 3, 2, 4, 1, 1, 13, 8, 2, 4, 3, 1, 1, 1, 1, 20, 2, 1, 1, 1, 2, 10, 1, 17, 2, 1, 4, 3, 2, 4, 1, 1, 1, 1, 10, 1, 7, 1, 3, 1, 10, 8, 2, 1, 2, 3, 12, 31, 1, 5, 1, 1, 8, 4, 1, 1, 1, 3, 1, 3, 3, 1, 3, 2, 1, 1, 15, 1, 9, 2, 1, 1, 2, 1, 2, 1, 1, 2, 2, 5, 8, 1, 3, 6, 1, 8, 18, 4, 36, 1, 1, 6, 4, 2, 3, 19, 1, 1, 1, 1, 3, 1, 2, 2, 15, 1, 12, 1, 8, 1, 6, 1, 1, 2, 1, 3, 1, 1, 2, 3, 2, 9, 11, 2, 1, 2, 10, 1, 2, 1, 4, 1, 3, 21, 1, 1, 1, 6, 5, 1, 6, 2, 4, 4, 11, 1, 6, 4, 2, 105, 3, 1, 5, 11, 1, 6, 2, 1, 4, 1, 3, 1, 12, 1, 4, 3, 11, 1, 1, 1, 1, 12, 7, 55, 1, 1, 11, 6, 1, 4, 1, 3, 3, 1, 1, 1, 1, 64, 1, 31, 1, 9, 1, 5, 18, 2, 1, 2, 32, 1, 2, 6, 5, 1, 1, 1, 1, 4, 9, 1, 1, 7, 1, 3, 1, 4, 2, 1, 1, 1, 1, 20, 1, 1, 1, 3, 1, 2, 66, 13, 1, 1, 1, 2, 5, 6, 1, 1, 1, 14, 1, 1, 1, 2, 2, 11, 8, 4, 1, 1, 1, 1, 8, 1, 2, 1, 18, 1, 2, 1, 3, 6, 1, 3, 21, 1, 8, 2, 15, 3, 1, 1, 1, 1, 5, 1, 2, 1, 23, 1, 1, 1, 5, 2, 6, 10, 1, 7, 1, 6, 10, 2, 1, 2, 2, 1, 1, 14, 1, 1, 1, 10, 3, 1, 19, 1, 26, 1, 1, 2, 10, 2, 5, 1, 10, 1, 25, 17, 1, 2, 4, 1, 4, 1, 1, 2, 1, 1, 209, 9, 1, 2, 3, 3, 18), integer_part=0)
    # SCF of root 2: FiniteSimpleContinuedFraction(partial_quotients=(1, 1, 1, 2, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 3, 34, 3, 8, 2, 1, 27, 1, 9, 1, 1, 6, 41, 14, 2, 35, 9, 1, 4, 5, 1, 12, 4, 1, 3, 1, 8, 1, 2, 2, 1, 1, 4, 1, 7, 1, 1, 7, 9, 2, 1, 1, 10, 1, 3, 2, 10, 13, 44, 29, 5, 3, 4, 4, 1, 409, 1, 1, 3, 1, 1, 34, 1, 13, 1, 1, 2, 1, 2, 4, 1, 1, 3, 1, 1, 7, 1, 19, 2, 1, 1, 18, 1, 2, 15, 1, 1, 1, 1, 44, 1, 1, 3, 15, 1, 6, 3, 1, 1, 184, 10, 3, 3, 18, 1, 4, 1, 2, 1, 13, 1, 15, 2, 4, 2, 2, 3, 2, 2, 1, 2, 2, 2, 1, 1, 6, 1, 4, 6, 1, 2, 2, 1, 2, 2, 1, 1, 1, 24, 1, 2, 15, 1, 1, 2, 7, 2, 1, 1, 3, 1, 13, 4, 5, 3, 19, 1, 1, 6, 5, 2, 3, 1, 1, 29, 1, 11, 6, 13, 1, 4, 26, 1, 1, 3, 4, 1, 6, 1, 1, 2, 10, 6, 1, 4, 1, 6, 6, 1, 2, 2, 1, 2, 5, 3, 8, 2, 1, 1, 10, 3, 7, 1, 2, 8, 23, 1, 4, 3, 1, 1, 1, 2, 28, 1, 6, 2, 2, 2, 2, 8, 2, 6, 3, 2, 2, 2, 5, 51, 1, 3, 3, 1, 8, 6, 2, 8, 2, 5, 32, 2, 1, 167, 1, 1, 1, 4, 4, 1, 9, 2, 1, 1, 408, 4, 1, 30, 1, 4, 24, 1, 2, 1, 1, 1, 9, 1, 10, 1, 1, 2, 1, 8, 1, 2, 2, 4, 3, 1, 1, 1, 4, 1, 3, 6, 1, 1, 3, 21, 3, 1, 1, 1, 11, 2, 6, 2642, 1, 1, 13, 1, 1, 6, 1, 3, 16, 1, 3, 1, 1, 2, 10, 1, 11, 318, 1, 1, 3, 1, 1, 15, 1, 9, 1, 17, 3, 3, 1, 1, 1, 1, 2, 2, 1, 1, 1, 11, 3, 5, 9, 5, 1, 5, 1, 6, 1, 1, 1, 4, 1, 9, 3, 5, 1, 6, 7, 4, 3, 1, 1, 2, 5, 2, 1, 35, 1, 1, 1, 1, 5, 2, 3, 6, 66, 3, 1, 1, 1, 12, 25, 2, 2, 1, 1, 8, 1, 1, 4, 11, 3, 9, 4, 1, 1, 1, 16, 1, 18, 1, 1, 6, 1, 6, 6, 1, 1, 5, 4, 6, 1, 5, 1, 2, 3, 1, 1, 1, 1, 1, 6, 1, 4, 7, 1, 5, 1, 3, 6, 3, 2, 2, 1, 8, 1, 2, 10, 5, 1, 8, 1, 1, 1, 5, 2, 10, 2, 4, 1, 4, 1, 1, 2, 3, 1, 1, 1, 1, 7, 7, 295, 24, 1, 1, 1, 24, 1, 1, 5, 3, 6, 1, 7, 1, 1, 9, 1, 6, 3, 1, 1, 8, 1, 2), integer_part=0)
        
    # pad1 = [1, 36]
    # cycle1 = [3, 8, 3, 34]
    # pscf1 = catena.PeriodicSimpleContinuedFraction(period=cycle1, pre_period=pad1, integer_part=0)
    # print(f"PSCF 1: {pscf1}")
    # print(f"PSCF 1 as decimal: {pscf1.convergent(100)[0] / pscf1.convergent(100)[1]}")
    # print(f"PSCF 1 quadratic coefficients: {pscf1.quadratic_coefficients()}")

    # pad2 = [1, 1, 1, 2]
    # cycle2 = [8, 3, 34, 3]
    # pscf2 = catena.PeriodicSimpleContinuedFraction(period=cycle2, pre_period=pad2, integer_part=0)
    # print(f"PSCF 2: {pscf2}")
    # print(f"PSCF 2 as decimal: {pscf2.convergent(100)[0] / pscf2.convergent(100)[1]}")
    # print(f"PSCF 2 quadratic coefficients: {pscf2.quadratic_coefficients()}")

    # pscf3 = pscf1 + 1 # make bigger than 1

    # print(f"PSCF 3: {pscf3}")
    # print(f"PSCF 3 as decimal: {pscf3.convergent(100)[0] / pscf3.convergent(100)[1]}")
    # print(f"PSCF 3 quadratic coefficients: {pscf3.quadratic_coefficients()}")

    # A, B, C = pscf3.quadratic_coefficients()
    # P = Decimal(-B)
    # D = Decimal(B)**2 - 4*Decimal(A)*Decimal(C)
    # Q = 2*Decimal(A)
    # X = (P + D.sqrt()) / Q
    # X_conjugate = (P - D.sqrt()) / Q
    # print(f"X: {X}")
    # print(f"Conjugate of X: {X_conjugate}")

    # pscf4 = catena.PeriodicSimpleContinuedFraction(period=cycle1, pre_period=[], integer_part=36)
    # print(f"PSCF 4: {pscf4}")
    # print(f"PSCF 4 as decimal: {pscf4.convergent(100)[0] / pscf4.convergent(100)[1]}")
    # print(f"PSCF 4 quadratic coefficients: {pscf4.quadratic_coefficients()}")

    # print(catena.FiniteSimpleContinuedFraction(partial_quotients=(1, 36, 3, 8, 3, 34, 3, 8,), integer_part=0).to_decimal())

    # import time

    # for P in range(-15, 16):
    #     for Q in range(-15, 16):
    #         if Q == 0:
    #             continue
    #         for D in range(1, 20):
    #             if isqrt(D)**2 == D:
    #                 continue
    #         print(f"\nTesting with P={P}, Q={Q}, D={D}:")
    #         t0 = time.perf_counter()
    #         result1 = catena.mathlib.convert.from_quadratic_surd_to_scf(P, Q, D)
    #         t1 = time.perf_counter()
    #         result2 = catena.mathlib.convert.from_quadratic_surd_to_conjugate_scf(P, Q, D)
    #         t2 = time.perf_counter()
    #         result3 = continued_fraction_periodic(P, Q, D)
    #         t3 = time.perf_counter()
    #         result4 = continued_fraction_periodic(P, Q, D, s=-1)
    #         t4 = time.perf_counter()

    #         result_3_copy, result_4_copy = result3, result4
    #         result3 = (result3[0], result3[1:-1], result3[-1])
    #         result4 = (result4[0], result4[1:-1], result4[-1])

    #         if result1 != result3 or result2 != result4:
    #             if (result2 != result3 or result1 != result4) and len(result_3_copy) > 1 and len(result_4_copy) > 1:
    #                 print(f"Discrepancy found for P={P}, Q={Q}, D={D}:")
    #                 print(f"from_quadratic_surd_to_scf:           {result1}  [{(t1-t0)*1e6:.2f} µs]")
    #                 print(f"continued_fraction_periodic:          {result3}  [{(t3-t2)*1e6:.2f} µs]")
    #                 print(f"from_quadratic_surd_to_conjugate_scf: {result2}  [{(t2-t1)*1e6:.2f} µs]")
    #                 print(f"continued_fraction_periodic (s=-1):   {result4}  [{(t4-t3)*1e6:.2f} µs]")


    #         # print(f"from_quadratic_surd_to_scf:           {result1}  [{(t1-t0)*1e6:.2f} µs]")
    #         # print(f"continued_fraction_periodic:          {result3}  [{(t3-t2)*1e6:.2f} µs]")
    #         # print(f"from_quadratic_surd_to_conjugate_scf: {result2}  [{(t2-t1)*1e6:.2f} µs]")
    #         # print(f"continued_fraction_periodic (s=-1):   {result4}  [{(t4-t3)*1e6:.2f} µs]")

    # pscf = catena.PeriodicSimpleContinuedFraction(period=[3, 8, 3, 34], pre_period=[1, 36], integer_part=0)
    # print(f"PSCF: {pscf}")
    # print(f"PSCF as decimal: {pscf.convergent(100)[0] / pscf.convergent(100)[1]}")
    # print(f"PSCF quadratic coefficients: {pscf.quadratic_coefficients()}")
    # print(f"PSCF surd form: {pscf.quadratic_surd()}")

    # conjugate = pscf.conjugate()
    # print(f"Conjugate of PSCF: {conjugate}")
    # print(f"Conjugate of PSCF as decimal: {conjugate.convergent(100)[0] / conjugate.convergent(100)[1]}")
    # print(f"Conjugate of PSCF quadratic coefficients: {conjugate.quadratic_coefficients()}")
    # print(f"Conjugate of PSCF surd form: {conjugate.quadratic_surd()}")
    
    # inverse = pscf.inverse()
    # print(f"Inverse of PSCF: {inverse}")
    # print(f"Inverse of PSCF as decimal: {inverse.convergent(100)[0] / inverse.convergent(100)[1]}")
    # print(f"Inverse of PSCF quadratic coefficients: {inverse.quadratic_coefficients()}")
    # print(f"Inverse of PSCF surd form: {inverse.quadratic_surd()}")

    # inverse_conjugate = inverse.conjugate()
    # print(f"Conjugate of the inverse of PSCF: {inverse_conjugate}")
    # print(f"Conjugate of the inverse of PSCF as decimal: {inverse_conjugate.convergent(100)[0] / inverse_conjugate.convergent(100)[1]}")
    # print(f"Conjugate of the inverse of PSCF quadratic coefficients: {inverse_conjugate.quadratic_coefficients()}")
    # print(f"Conjugate of the inverse of PSCF surd form: {inverse_conjugate.quadratic_surd()}")

    
    
    # # pscf2 = catena.PeriodicSimpleContinuedFraction(period=(8, 3, 34, 3), pre_period=(1, 1, 1, 2), integer_part=0)
    # # print(f"PSCF 2: {pscf2}")
    # # print(f"PSCF 2 as decimal: {pscf2.convergent(100)[0] / pscf2.convergent(100)[1]}")
    # # print(f"PSCF 2 quadratic coefficients: {pscf2.quadratic_coefficients()}")
    # # print(f"PSCF 2 surd form: {pscf2.quadratic_surd()}")

    # # conjugate_pscf2 = pscf2.conjugate()
    # # print(f"Conjugate of PSCF 2: {conjugate_pscf2}")
    # # print(f"Conjugate of PSCF 2 as decimal: {conjugate_pscf2.convergent(100)[0] / conjugate_pscf2.convergent(100)[1]}")
    # # print(f"Conjugate of PSCF 2 quadratic coefficients: {conjugate_pscf2.quadratic_coefficients()}")
    # # print(f"Conjugate of PSCF 2 surd form: {conjugate_pscf2.quadratic_surd()}")

    # # inverse_pscf2 = pscf2.inverse()
    # # print(f"Inverse of PSCF 2: {inverse_pscf2}")
    # # print(f"Inverse of PSCF 2 as decimal: {inverse_pscf2.convergent(100)[0] / inverse_pscf2.convergent(100)[1]}")
    # # print(f"Inverse of PSCF 2 quadratic coefficients: {inverse_pscf2.quadratic_coefficients()}")
    # # print(f"Inverse of PSCF 2 surd form: {inverse_pscf2.quadratic_surd()}")

    # sqer2 = catena.PeriodicSimpleContinuedFraction(period=(2,), pre_period=(), integer_part=1)
    # print(f"Square root of 2 as PSCF: {sqer2}")
    # print(f"Square root of 2 as decimal: {sqer2.convergent(100)[0] / sqer2.convergent(100)[1]}")
    # print(f"Square root of 2 quadratic coefficients: {sqer2.quadratic_coefficients()}")
    # print(f"Square root of 2 surd form: {sqer2.quadratic_surd()}") 

    # inverse_sqrt2 = sqer2.inverse()
    # print(f"Inverse of square root of 2 as PSCF: {inverse_sqrt2}")
    # print(f"Inverse of square root of 2 as decimal: {inverse_sqrt2.convergent(100)[0] / inverse_sqrt2.convergent(100)[1]}")
    # print(f"Inverse of square root of 2 quadratic coefficients: {inverse_sqrt2.quadratic_coefficients()}")
    # print(f"Inverse of square root of 2 surd form: {inverse_sqrt2.quadratic_surd()}")

    # inverse_conjugate_sqrt2 = inverse_sqrt2.conjugate()
    # print(f"Conjugate of the inverse of square root of 2 as PSCF: {inverse_conjugate_sqrt2}")
    # print(f"Conjugate of the inverse of square root of 2 as decimal: {inverse_conjugate_sqrt2.convergent(100)[0] / inverse_conjugate_sqrt2.convergent(100)[1]}")
    # print(f"Conjugate of the inverse of square root of 2 quadratic coefficients: {inverse_conjugate_sqrt2.quadratic_coefficients()}")
    # print(f"Conjugate of the inverse of square root of 2 surd form: {inverse_conjugate_sqrt2.quadratic_surd()}")

    # print(x:=catena.FiniteSimpleContinuedFraction.from_rational((355, 113)))
    # print(x.generator)
    # M = 0 
    # for _ in range(10000):
    #     rscf = random_fscf()
    #     plateau_order = find_plateau_order(rscf)
    #     if plateau_order > M:
    #         M = plateau_order
    #         print(f"Random FSCF: {rscf}")
    #         print(f"Plateau order: {find_plateau_order(rscf)}")

    # print(find_plateau_order(catena.FiniteSimpleContinuedFraction.from_float(0.000000000009732050807568877)))

    # phi = catena.PeriodicSimpleContinuedFraction(period=(1,), pre_period=(), integer_part=0)

    # for i in range(10):
    #     print(f"Tail convergent {i}: {phi.tail_convergent(i)}")
    #     print(f"Convergent {i}: {phi.convergent(i)}")

    # _str = catena.strings.safe_int_str
    # print(f"Tail convergent 100,000: {tuple(map(_str, phi.tail_convergent(100_000)))}")
    # print(f"Tail convergent 100,000: {tuple(map(_str, phi.convergent(100_000)))}")
    # phi = catena.PeriodicSimpleContinuedFraction(period=(1,), pre_period=(), integer_part=0)
    
    # for k in range(0, 100):
    #     c_k = phi.convergent(k)
    #     c_next = phi.convergent(k+1)
    #     c_next2 = phi.convergent(k+2)
    #     # print(f"Determinant of convergents {k} and {k+1}: {c_k[0]*c_next[1] - c_k[1]*c_next[0]}")
    #     # print(f"Difference between convergents {k} and {k+2}: {(c_k[0]*c_next2[1] - c_k[1]*c_next2[0])}")
    #     print(f"Value of q_{k} * q_{k+1}: {c_k[1]} * {c_next[1]} = {c_k[1] * c_next[1]}. Bigger than e17: {c_k[1] * c_next[1] > 10**17}")
        # print(f"Value of convergent {k}: {c_k[0]/c_k[1]}")

    # for k in range(1, 100, 2):
    #     c_k = phi.convergent(k)
    #     c_next = phi.convergent(k+1)
    #     print(f"Value of convergent {k}: {c_k[0]/c_k[1]}")

    # u = [1, 2, 3, 4, 5]
    # v = [5, 4, 3, 2, 2]
    # v0 = v[0]
    # v_ = v[1:]

    # scf_u = catena.FiniteSimpleContinuedFraction(partial_quotients=u, integer_part=0)
    # scf_v = catena.FiniteSimpleContinuedFraction(partial_quotients=v, integer_part=0)
    # scf_v_ = catena.FiniteSimpleContinuedFraction(partial_quotients=v_, integer_part=0)
    # scf_uv = catena.FiniteSimpleContinuedFraction(partial_quotients=u+v, integer_part=0)

    # _, q_u = scf_u.terminal_convergent
    # p_v_, q_v_ = scf_v_.terminal_convergent

    # q_u = scf_u.terminal_convergent[1]
    # q_u1 = scf_u.convergent(len(u)-2)[1]
    # q_v = v0*q_v_ + p_v_

    # print(f"q_v vs real q_v: {q_v} vs {scf_v.terminal_convergent[1]}")

    # q_uv = q_u*q_v + q_u1*q_v_
    # print(f"q_uv vs real q_uv: {q_uv} vs {scf_uv.terminal_convergent[1]}")


    # phi = catena.PeriodicSimpleContinuedFraction(period=(1,), pre_period=(), integer_part=0)

    # print(float(phi))

    # print((-phi,))

    # # c = Fraction(*phi.convergent(50))
    # # inv = 1-c

    # # phi_inv = catena.FiniteSimpleContinuedFraction.from_rational(inv)
    # # print(f"Inverse of phi as FSCF: {phi_inv}")

    # # sqrt2_frac = catena.PeriodicSimpleContinuedFraction(period=(2,), pre_period=(), integer_part=0)

    # # c2 = Fraction(*sqrt2_frac.convergent(50))
    # # inv2 = 1 - c2
    # # sqrt2_inv = catena.FiniteSimpleContinuedFraction.from_rational(inv2)
    # # print(f"Inverse of sqrt(2) as FSCF: {sqrt2_inv}")


    # # periodic = catena.PeriodicSimpleContinuedFraction(period=(1, 2, 3), pre_period=(4, 5), integer_part=0)
    # finite = catena.FiniteSimpleContinuedFraction(partial_quotients=(1,), integer_part=0)
    # print(finite)
    # print(-finite)
    # # inserted = periodic.generator.insert(finite.generator, 2)
    # # print(f"Inserted generator: {inserted}")
    # # print(f"First 40 partial quotients of inserted generator: {tuple(inserted(i) for i in range(40))}")

    # print(float(finite))
    # print(float(-finite))

    # print(f"Negate finite by negating is value as Fraction and converting back to FSCF: {(y:=catena.FiniteSimpleContinuedFraction.from_rational(-Fraction(*finite.terminal_convergent)))}")

    # print(f"Float of negated finite: {float(y)}")

    # print(float(catena.constants.e))

    # for i in range(10):
    #     print(f"{i}-th partial quotient of e: {catena.constants.e.generator(i)}")
    # seed = catena.numbers.randoms.Seed(42)
    # # random scf
    # for i in range(100):
    #     r = print(catena.numbers.randoms.GaussKuzminSCF().periodic_scf(5, 4))

    # r = catena.numbers.randoms.GaussKuzminSCF().periodic_scf(5, 4)

    # print(r)
    # print()
    # print(r.inverse().conjugate())
    # print(r.conjugate().inverse())

    # q = catena.PeriodicSimpleContinuedFraction.from_quadratic_surd(1, 1, 2)
    # print(q.quadratic_surd())
    # print(q.is_principal_surd())
    # q_inv = q.inverse()
    # print(q_inv.quadratic_surd())
    # print(q_inv.is_principal_surd())

    # p = catena.PeriodicSimpleContinuedFraction.from_quadratic_surd(5, 1, 7)
    # print(p.quadratic_surd())
    # print(p.is_principal_surd())
    # p_inv = p.inverse()
    # print(p_inv.quadratic_surd())
    # print(p_inv.is_principal_surd())

    for P in range(-15, 16):
        for Q in range(-15, 16):
            if Q == 0:
                continue
            for D in range(1, 20):
                if isqrt(D)**2 == D:
                    continue
                print(f"\nTesting with P={P}, Q={Q}, D={D}:")
                result = catena.PeriodicSimpleContinuedFraction.from_quadratic_surd(P, Q, D)
                print(f"Result: {result}")
                print(f"Quadratic surd form: {result.quadratic_surd()}")

    #print(catena.PeriodicSimpleContinuedFraction.from_quadratic_surd(-15, -6, 10))