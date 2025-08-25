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
from typing import List, Dict

PHI = (1 + 5 ** 0.5) / 2.0
ELEMENTS_CN = ["金", "木", "水", "火", "土"]
ELEMENTS_PY = ["J", "M", "S", "H", "T"]  # short initials

def cents(f: float, ref: float) -> float:
    return 1200.0 * math.log(f / ref, 2.0)

class PetersenScale:
    def __init__(self,
                 F_base: float = 20.0,
                 delta_theta: float = 4.8,   # degrees
                 F_min: float = 30.0,
                 F_max: float = 6000.0,
                 reference: float = 440.0):
        self.F_base = float(F_base)
        self.delta_theta = float(delta_theta)
        self.F_min = float(F_min)
        self.F_max = float(F_max)
        self.reference = float(reference)

    def _theta_for(self, e: int, p: int) -> float:
        # p in {-1,0,1}, p=-1 corresponds to baseline theta_e
        theta_e = 72.0 * e
        return theta_e + (p + 1) * self.delta_theta

    def _u_from_theta(self, theta: float) -> float:
        # map theta modulo 360 deg into [0,1)
        mod = theta % 360.0
        return mod / 360.0

    def _n_range_for_u(self, u: float) -> (int, int):
        # compute integer n range so that F_base * phi^(n+u) in [F_min, F_max]
        lo = math.log(self.F_min / self.F_base, PHI) - u
        hi = math.log(self.F_max / self.F_base, PHI) - u
        n_min = math.ceil(lo)
        n_max = math.floor(hi)
        return n_min, n_max

    def _zone_interval(self, n: int) -> (float, float):
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

    def generate(self) -> List[Dict]:
        out = []
        for e in range(5):
            for p in (-1, 0, 1):
                theta = self._theta_for(e, p)
                u = self._u_from_theta(theta)
                n_min, n_max = self._n_range_for_u(u)
                # iterate n in range and produce entries (clipped by F_min/F_max)
                for n in range(n_min, n_max + 1):
                    f = self.F_base * (PHI ** (n + u))
                    if f < self.F_min - 1e-12 or f > self.F_max + 1e-12:
                        continue
                    a, b = self._zone_interval(n)
                    # clip interval to global bounds for presentation
                    Ia = max(a, self.F_min)
                    Ib = min(b, self.F_max)
                    entry = {
                        "e": e,
                        "p": p,
                        "theta_deg": round(theta, 6),
                        "u": round(u, 6),
                        "n": n,
                        "interval_a": round(Ia, 6),
                        "interval_b": round(Ib, 6),
                        "freq": round(f, 6),
                        "cents_ref": round(cents(f, self.reference), 4),
                        "key_short": self.key_name_short(e, p),
                        "key_long": self.key_name_long(e, p)
                    }
                    out.append(entry)
        # sort by frequency ascending
        out.sort(key=lambda x: x["freq"])
        return out

    def export_csv(self, path: str, entries: List[Dict] = None) -> None:
        if entries is None:
            entries = self.generate()
        fieldnames = ["key_short", "key_long", "e", "p", "n",
                      "theta_deg", "u", "interval_a", "interval_b",
                      "freq", "cents_ref"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in entries:
                w.writerow({k: r.get(k, "") for k in fieldnames})

if __name__ == "__main__":
    scale = PetersenScale(F_base=20.0, delta_theta=4.8, F_min=30.0, F_max=6000.0, reference=220.0)
    entries = scale.generate()
    # 打印前三条和总数
    for e in entries[:6]:
        print(f"{e['key_short']:4} {e['key_long']:<6} n={e['n']:>2} freq={e['freq']:8.3f} Hz  interval=[{e['interval_a']:.3f},{e['interval_b']:.3f}] cents={e['cents_ref']}")
    print(f"... total entries: {len(entries)}")
    # 导出 CSV（可修改路径）
    try:
        scale.export_csv("petersen_phi_scale.csv", entries)
        print("exported petersen_phi_scale.csv")
    except Exception as ex:
        print("CSV export failed:", ex)