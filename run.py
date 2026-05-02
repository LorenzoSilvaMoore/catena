import catena
from decimal import Decimal, getcontext
from fractions import Fraction

from math import gcd, isqrt

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

    for P in range(-15, 16):
        for Q in range(-15, 16):
            if Q == 0:
                continue
            for D in range(1, 20):
                if isqrt(D)**2 == D:
                    continue

                if Q < 0:
                    P = -P
                    Q = -Q

                X = (Decimal(P) + Decimal(D).sqrt()) / Decimal(Q)
                
                # Transform the surd into a quadratic form
                P0 = P * 2 * Q
                Q0 = Q * 2 * Q
                D0 = D * 4 * Q**2
                A = Q * Q
                B = -P0
                C = (P0**2 - D0) // (4 * Q * Q)
                g = gcd(A, B, C)
                A, B, C = Decimal(A // g), Decimal(B // g), Decimal(C // g)
                x0 = (-B + Decimal(B**2 - 4 * A * C).sqrt()) / (2 * A)
                x1 = (-B - Decimal(B**2 - 4 * A * C).sqrt()) / (2 * A)

                if 6 < x0 and 4 < x1:
                    print(f"P={P}, Q={Q}, D={D} => X={float(X)}")
                    print(f"Quadratic form: {A}x^2 + {B}x + {C} = 0")
                    print(f"Roots: {float(x0)}, {float(x1)}")
                    print("Both roots are greater than 1 in absolute value, skipping.")
                    
                    scf1 = catena.FiniteSimpleContinuedFraction.from_decimal(str(x0))
                    scf2 = catena.FiniteSimpleContinuedFraction.from_decimal(str(x1))
                    print(f"SCF of root 1: {scf1}")
                    print(f"SCF of root 2: {scf2}")
                    

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


    