import hashlib
import math
from decimal import Decimal, localcontext

from typing import Callable, Optional

from abc import ABC, abstractmethod
from ..catena import (
    SimpleContinuedFraction,
    FiniteSimpleContinuedFraction,
    PeriodicSimpleContinuedFraction,
)
from ..generators import (
    Generator,
    CachedGenerator,
    FiniteGenerator,
    PeriodicGenerator,
)

import uuid


class Seed:
    def __init__(self, initial_state: Optional[str|int] = None):
        self._state = str(initial_state).encode() if initial_state is not None else str(uuid.uuid4()).encode()
        self._step = 0
        self._initial_state = self._state

    @property
    def state(self) -> bytes:
        _state = self._state
        self._state = hashlib.sha256(self._state).digest()
        self._step += 1
        return _state
    
    @property
    def initial_state(self) -> bytes:
        return self._initial_state
    
    @property
    def step(self) -> int:
        return self._step
    
    @property
    def current_state(self) -> bytes:
        return self._state
    
    def __str__(self):
        return f"Seed(initial_state={self._initial_state.decode()}, step={self._step})"
    
    
_SEED = Seed()  # global seed for default random generators


# --- SHA-256 based (O(1), cryptographic uniformity) ---
class GaussKuzminSHA:
    def __init__(self, seed: Optional[str|int|bytes] = None):
        if isinstance(seed, bytes):
            self._seed = seed
        else:
            self._seed = str(seed).encode() if seed is not None else str(uuid.uuid4()).encode()

    def _uniform(self, n: int) -> float:
        h = hashlib.sha256(self._seed + n.to_bytes(8, 'big')).digest()
        bits = int.from_bytes(h[:7], 'big') >> 3  # 53 bits
        return bits / (1 << 53)

    def __call__(self, n: int) -> int:
        u = self._uniform(n)
        return int(1 / (2**u - 1))  # Gauss-Kuzmin distribution via uniform transform
    
    @property
    def __name__(self):
        return f"GaussKuzminSHA(seed={self._seed.decode()})"
    

class UniformSHAArbitrary:
    def __init__(self, precision: int = 50):
        """
        seed      : any value (converted to str then bytes)
        precision : number of significant decimal digits in the output
        """
        self._precision = precision
        # bits needed to represent precision decimal digits
        bits_needed = math.ceil(precision * math.log2(10)) + 1
        # SHA-256 gives 256 bits per round
        self._n_rounds = math.ceil(bits_needed / 256)
        self._total_bits = self._n_rounds * 256
        self._divisor = 1 << self._total_bits  # exact Python int — avoid Decimal precision issues at init

    def __call__(self, seed: bytes, n: int) -> Decimal:
        with localcontext() as ctx:  # thread-local copy; caller's context restored on exit
            ctx.prec = self._precision + 10  # guard digits

            # Build the hash chain
            h = hashlib.sha256(seed + n.to_bytes(8, 'big')).digest()
            raw = bytearray(h)
            for _ in range(self._n_rounds - 1):
                h = hashlib.sha256(h).digest()
                raw += h

            big_int = int.from_bytes(raw, 'big')
            result = Decimal(big_int) / Decimal(self._divisor)  # Decimal(int) is always exact
            ctx.prec = self._precision  # drop guard digits
            return +result  # quantizes to self._precision before exiting the block
        
    @property
    def __name__(self):
        return f"UniformSHAArbitrary(precision={self._precision})"
        

class GaussKuzminSHAArbitrary:
    def __init__(self, seed: Optional[str|int|bytes] = None, precision: int = 50):
        if isinstance(seed, bytes):
            self._seed = seed
        else:
            self._seed = str(seed).encode() if seed is not None else str(uuid.uuid4()).encode()
        self._uniform = UniformSHAArbitrary(precision)

    def __call__(self, n: int) -> int:
        u = self._uniform(seed=self._seed, n=n)
        with localcontext() as ctx:
            ctx.prec = self._uniform._precision + 10  # guard digits
            result = int(1 / (2**u - 1))  # Gauss-Kuzmin distribution via uniform transform
            return result
        
    @property
    def __name__(self):
        return f"GaussKuzminSHAArbitrary(seed={self._seed.decode()}, precision={self._uniform._precision})"
        
        

class RandomSCF(ABC):    
    @abstractmethod
    def __make_callable__(self) -> Callable:
        pass

    def generator(self) -> Generator:
        return Generator(self.__make_callable__())
    
    def cached_generator(self) -> CachedGenerator:
        return CachedGenerator(self.__make_callable__())
    
    def finite_generator(self, size: int) -> FiniteGenerator:
        func = self.__make_callable__()
        data = [func(i) for i in range(size)]
        return FiniteGenerator(data)
    
    def periodic_generator(self, period_size: int, pre_period_size: int = 0) -> PeriodicGenerator:
        func = self.__make_callable__()
        period = [func(i) for i in range(period_size)]
        pre_period = [func(i+period_size) for i in range(pre_period_size)]
        return PeriodicGenerator(period, pre_period)
    
    def scf(self, integer_part: int = 0, memoised=False) -> SimpleContinuedFraction:
        if memoised is True:
            return SimpleContinuedFraction(self.cached_generator(), integer_part=integer_part)
        
        return SimpleContinuedFraction(self.generator(), integer_part=integer_part)
    
    def finite_scf(self, size: int, integer_part: int = 0) -> FiniteSimpleContinuedFraction:
        return FiniteSimpleContinuedFraction(self.finite_generator(size), integer_part=integer_part)
    
    def periodic_scf(self, period_size: int, pre_period: int = 0, integer_part: int = 0) -> PeriodicSimpleContinuedFraction:
        return PeriodicSimpleContinuedFraction(self.periodic_generator(period_size, pre_period), integer_part=integer_part)
    

class GaussKuzminSCF(RandomSCF):
    def __init__(self, seed: Optional[Seed] = None):
        self._seed = seed or _SEED

    def __make_callable__(self) -> Callable:
        return GaussKuzminSHA(self._seed.state)


class GaussKuzminArbitrarySCF(RandomSCF):
    def __init__(self, precision: int = 50, seed: Optional[Seed] = None,):
        self._seed = seed or _SEED
        self._precision = precision

    def __make_callable__(self) -> Callable:
        return GaussKuzminSHAArbitrary(self._seed.state, self._precision)