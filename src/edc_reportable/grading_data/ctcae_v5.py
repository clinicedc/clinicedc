"""
https://ctep.cancer.gov/protocoldevelopment/electronic_applications/docs/CTCAE_v5_Quick_Reference_8.5x11.pdf
Gamma GT
U/L

Male: 12 <= x <= 64
G1 64 < x <= 160
G2 160 < x <= 320
G3 320 < x <= 1280
G4 x > 1280

Female: 9 - 36
>36 -≤90
>90 -≤180
>180 -≤720
>720

>ULN - 2.5 x ULN if baseline was normal; 2.0 - 2.5 x baseline if baseline was abnormal
>2.5 - 5.0 x ULN if baseline was normal; >2.5 - 5.0 x baseline if baseline was abnormal
>5.0 - 20.0 x ULN if baseline was normal; >5.0 - 20.0 x baseline if baseline was abnormal
>20.0 x ULN if baseline was normal; >20.0 x baseline if baseline was abnormal
"""
from edc_constants.constants import FEMALE, MALE

from ..adult_age_options import adult_age_options
from ..constants import GRADE1, GRADE2, GRADE3, GRADE4
from ..parsers import parse as p
from ..units import IU_LITER

ggt_baseline_normal = (
    [
        p(
            "2.50*ULN<x<=2.50*ULN",
            grade=GRADE1,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "2.50*ULN<=x<5.00*ULN",
            grade=GRADE2,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "5.00*ULN<=x<10.00*ULN",
            grade=GRADE3,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
        p(
            "10.00*ULN<=x",
            grade=GRADE4,
            units=IU_LITER,
            gender=[MALE, FEMALE],
            **adult_age_options,
        ),
    ],
)
