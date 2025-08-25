"""
Petersen 黄金率音区模块（库形式）
提供：基点 -> 按 phi 划分音区 -> 在每区内按五行-阴阳角度放置 15 个音位
API 要点：
  - PetersenScale(F_base=20, delta_theta=4.8, F_min=30, F_max=6000)
  - scale.generate() -> list of entries (dict): {e,p,theta,u,n,interval,freq,cents,key_short,key_long}
  - scale.export_csv(path)
短名建议：元素拼音首字母 + 极性符号（-, 0, +），例如 J- / J0 / J+
长名：中文元素 + 极性（例如 "金 阴"）
"""
from __future__ import annotations

import math
import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union

# 采用缓存以提高性能（如果频繁调用）
from functools import lru_cache

PHI = (1 + 5 ** 0.5) / 2.0
ELEMENTS_CN = ["金", "木", "水", "火", "土"]
ELEMENTS_PY = ["J", "M", "S", "H", "T"]  # short initials

def cents(f: float, ref: float) -> float:
    # use log2 for cents (clearer / faster)
    return 1200.0 * math.log2(f / ref)

@dataclass
class ScaleEntry:
    e: int
    p: int
    theta_deg: float
    u: float
    n: int
    interval_a: float
    interval_b: float
    freq: float
    cents_ref: float
    key_short: str
    key_long: str

class PetersenScale:
    def __init__(self,
                 F_base: float = 20.0,
                 delta_theta: float = 4.8,   # degrees
                 F_min: float = 30.0,
                 F_max: float = 6000.0,
                 reference: float = 440.0):
        # basic validation
        if F_base <= 0 or F_min <= 0 or F_max <= 0:
            raise ValueError("F_base, F_min, F_max must be positive")
        if F_min >= F_max:
            raise ValueError("F_min must be less than F_max")
        self.F_base = float(F_base)
        self.delta_theta = float(delta_theta)
        self.F_min = float(F_min)
        self.F_max = float(F_max)
        self.reference = float(reference)
        self.logger = logging.getLogger(__name__)

    def _theta_for(self, e: int, p: int) -> float:
        # p in {-1,0,1}, p=-1 corresponds to baseline theta_e
        theta_e = 72.0 * e
        return theta_e + (p + 1) * self.delta_theta

    def _u_from_theta(self, theta: float) -> float:
         # map theta modulo 360 deg into [0,1)
        mod = theta % 360.0
        return mod / 360.0

    def _n_range_for_u(self, u: float) -> Tuple[int, int]:
        # compute integer n range so that F_base * phi^(n+u) in [F_min, F_max]
        lo = math.log(self.F_min / self.F_base, PHI) - u
        hi = math.log(self.F_max / self.F_base, PHI) - u
        n_min = math.ceil(lo)
        n_max = math.floor(hi)
        return n_min, n_max

    def _zone_interval(self, n: int) -> Tuple[float, float]:
        a = self.F_base * (PHI ** n)
        b = self.F_base * (PHI ** (n + 1))
        # clip to global bounds if desired downstream; here return raw
        return a, b

    def key_name_short(self, e: int, p: int) -> str:
        # short: initial + polarity symbol
        py = ELEMENTS_PY[e]
        sym = { -1: "-", 0: "0", 1: "+" }[p]
        return f"{py}{sym}"

    def key_name_long(self, e: int, p: int) -> str:
        el = ELEMENTS_CN[e]
        pol = { -1: "阴", 0: "中", 1: "阳" }[p]
        return f"{el} {pol}"

    def generate_raw(self) -> List[ScaleEntry]:
        """Generate raw ScaleEntry list with full precision (no rounding)."""
        out: List[ScaleEntry] = []
        for e in range(5):
            for p in (-1, 0, 1):
                theta = self._theta_for(e, p)
                u = self._u_from_theta(theta)
                n_min, n_max = self._n_range_for_u(u)
                for n in range(n_min, n_max + 1):
                    f = self.F_base * (PHI ** (n + u))
                    # clip by global bounds with tiny tolerance for floating errors
                    if f < self.F_min - 1e-12 or f > self.F_max + 1e-12:
                        continue
                    a, b = self._zone_interval(n)
                    Ia = max(a, self.F_min)
                    Ib = min(b, self.F_max)
                    entry = ScaleEntry(
                        e=e,
                        p=p,
                        theta_deg=theta,
                        u=u,
                        n=n,
                        interval_a=Ia,
                        interval_b=Ib,
                        freq=f,
                        cents_ref=cents(f, self.reference),
                        key_short=self.key_name_short(e, p),
                        key_long=self.key_name_long(e, p)
                    )
                    out.append(entry)
        out.sort(key=lambda x: x.freq)
        return out

    def generate(self, round_digits: Optional[int] = 6) -> List[Dict]:
        """
        Backward-compatible generator.
        By default rounds numeric fields to 6 decimals (freq) / 4 decimals (cents).
        If round_digits is None, raw floats are returned (as dicts converted from ScaleEntry).
        """
        raw = self.generate_raw()
        if round_digits is None:
            return [r.__dict__ for r in raw]
        rounded: List[Dict] = []
        for r in raw:
            rounded.append({
                "e": r.e,
                "p": r.p,
                "theta_deg": round(r.theta_deg, round_digits),
                "u": round(r.u, round_digits),
                "n": r.n,
                "interval_a": round(r.interval_a, round_digits),
                "interval_b": round(r.interval_b, round_digits),
                "freq": round(r.freq, round_digits),
                "cents_ref": round(r.cents_ref, 4),
                "key_short": r.key_short,
                "key_long": r.key_long
            })
        return rounded

    def frequencies_only(self) -> List[float]:
        """Return sorted list of frequencies (raw floats)."""
        return [e.freq for e in self.generate_raw()]

    @lru_cache(maxsize=128)
    def _cached_phi_power(self, exponent: float) -> float:
        """Cache phi powers for better performance with repeated calls."""
        return PHI ** exponent
    
    # 便利方法
    def get_frequency_for_key(self, key_short: str) -> Optional[float]:
        """Get frequency by key name (e.g., 'J-', 'M0', 'T+')."""
        for entry in self.generate_raw():
            if entry.key_short == key_short:
                return entry.freq
        return None
    
    def get_entries_in_zone(self, n: int) -> List[ScaleEntry]:
        """Get all entries in a specific zone n."""
        return [e for e in self.generate_raw() if e.n == n]
    
    def get_frequency_range(self) -> Tuple[float, float]:
        """Get actual min/max frequencies generated."""
        entries = self.generate_raw()
        if not entries:
            return (0.0, 0.0)
        freqs = [e.freq for e in entries]
        return (min(freqs), max(freqs))
    
    # 验证方法
    def validate_implementation(self) -> bool:
        """Verify the implementation matches document formulas."""
        # Test a few known cases
        test_cases = [
            (0, -1),  # 金阴: θ=0°, u=0
            (1, 0),   # 木中: θ=76.8°
            (4, 1),   # 土阳: θ=297.6°
        ]
        
        for e, p in test_cases:
            theta = self._theta_for(e, p)
            u = self._u_from_theta(theta)
            expected_theta = 72.0 * e + (p + 1) * self.delta_theta
            expected_u = (expected_theta % 360.0) / 360.0
            
            if abs(theta - expected_theta) > 1e-10:
                return False
            if abs(u - expected_u) > 1e-10:
                return False
        return True

    # 支持不同的输出格式
    def to_scala_file(self, path: Union[str, Path], description: str = "Petersen Golden Ratio Scale") -> None:
        """Export to Scala (.scl) format for music software."""
        entries = self.generate_raw()
        p = Path(path)
        
        with p.open("w", encoding="utf-8") as f:
            f.write(f"! {description}\n")
            f.write(f"{len(entries)}\n")
            f.write("!\n")
            
            for entry in sorted(entries, key=lambda x: x.freq):
                ratio = entry.freq / self.reference
                f.write(f"{ratio:.10f}\n")

    def export_csv(self, path: Union[str, Path], entries: Optional[List[Union[ScaleEntry, Dict]]] = None) -> None:
        if entries is None:
            entries = self.generate()
        p = Path(path)
        fieldnames = ["key_short", "key_long", "e", "p", "n",
                      "theta_deg", "u", "interval_a", "interval_b",
                      "freq", "cents_ref"]
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in entries:
                if isinstance(r, ScaleEntry):
                    row = r.__dict__
                else:
                    row = r
                w.writerow({k: row.get(k, "") for k in fieldnames})

if __name__ == "__main__":
    # quick smoke test
    scale = PetersenScale(F_base=20.0, delta_theta=4.8, F_min=30.0, F_max=6000.0, reference=220.0)
    entries = scale.generate()
    for e in entries[:6]:
        print(f"{e['key_short']:4} {e['key_long']:<6} n={e['n']:>2} freq={e['freq']:8.3f} Hz  interval=[{e['interval_a']:.3f},{e['interval_b']:.3f}] cents={e['cents_ref']}")
    print(f"... total entries: {len(entries)}")
    try:
        scale.export_csv("petersen_phi_scale.csv", entries)
        print("exported petersen_phi_scale.csv")
    except Exception as ex:
        print("CSV export failed:", ex)