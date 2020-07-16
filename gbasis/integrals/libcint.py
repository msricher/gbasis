r"""
Python C-API bindings for ``libcint`` GTO integrals library.

"""

from ctypes import CDLL, cdll, c_int, c_double, c_void_p
from ctypes.util import find_library

from numpy.ctypeslib import load_library, ndpointer


LIBCINT_USER_PATH: str = '/CHANGE/ME/libcint/build'
r"""
User-specified path where ``libcint`` shared object library may be located.

This module will look for ``libcint`` in the system's standard library paths first, and if the
library is not found, will then look in this directory.

"""


# Constants from cint.h
PTR_LIGHT_SPEED = 0
PTR_COMMON_ORIG = 1
PTR_RINV_ORIG = 4
PTR_RINV_ZETA = 7

# Omega parameter in range-separated coulomb operator erf(omega*r12)/r12
PTR_RANGE_OMEGA = 8

# Yukawa potential and slater-type geminal e^{-zeta r}
PTR_F12_ZETA = 9

# Gaussian type geminal e^{-zeta r^2}
PTR_GTG_ZETA = 10
PTR_ENV_START = 20

# Slots of atm
CHARGE_OF = 0
PTR_COORD = 1
NUC_MOD_OF = 2
PTR_ZETA = 3
PTR_FRAC_CHARGE = 3
RESERVE_ATMLOT1 = 4
RESERVE_ATMLOT2 = 5
ATM_SLOTS = 6

# Slots of bas
ATOM_OF = 0
ANG_OF = 1
NPRIM_OF = 2
NCTR_OF = 3
KAPPA_OF = 4
PTR_EXP = 5
PTR_COEFF = 6
RESERVE_BASLOT = 7
BAS_SLOTS = 8

# Slots of gout
POSX = 0
POSY = 1
POSZ = 2
POS1 = 3
POSXX = 0
POSYX = 1
POSZX = 2
POS1X = 3
POSXY = 4
POSYY = 5
POSZY = 6
POS1Y = 7
POSXZ = 8
POSYZ = 9
POSZZ = 10
POS1Z = 11
POSX1 = 12
POSY1 = 13
POSZ1 = 14
POS11 = 15

# Tensor
TSRX = 0
TSRY = 1
TSRZ = 2
TSRXX = 0
TSRXY = 1
TSRXZ = 2
TSRYX = 3
TSRYY = 4
TSRYZ = 5
TSRZX = 6
TSRZY = 7
TSRZZ = 8

# Some other boundaries
ANG_MAX = 12
POINT_NUC = 1
GAUSSIAN_NUC = 2
FRAC_CHARGE_NUC = 3


class LibCInt:
    r"""
    ``libcint`` shared object library helper class.

    """

    try:
        # Search for libcint in the system library paths
        _libcint_sys_path = find_library('cint')
        if _libcint_sys_path is None:
            raise OSError
        _libcint_cdll = cdll.LoadLibrary(_libcint_sys_path)
    except OSError:
        # If not found, try the user-specified path
        _libcint_cdll = load_library('libcint', LIBCINT_USER_PATH)

    _libcint: CDLL = _libcint_cdll
    r"""
    ``libcint`` shared object library.

    """

    def __getattr__(self, attr):
        r"""
        Helper for returning function pointers from ``libcint`` with proper signatures.

        """
        cfunc = getattr(self._libcint, attr)

        if attr == 'CINTlen_cart':
            cfunc.argtypes = [c_int]
            cfunc.restype = c_int

        elif attr == 'CINTlen_spinor':
            cfunc.argtypes = [
                c_int,
                ndpointer(dtype=c_int, ndim=1, flags=('C_CONTIGUOUS',)),
                ]
            cfunc.restype = c_int

        elif attr == 'CINTgto_norm':
            cfunc.argtypes = [c_int, c_double]
            cfunc.restype = c_double

        elif attr.startswith('CINTcgto') or attr.startswith('CINTtot'):
            cfunc.argtypes = [
                ndpointer(dtype=c_int, ndim=1, flags=('C_CONTIGUOUS',)),
                c_int,
                ]
            cfunc.restype = c_int

        elif attr.startswith('CINTshells'):
            cfunc.argtypes = [
                ndpointer(dtype=c_int, ndim=1, flags=('C_CONTIGUOUS', 'WRITEABLE')),
                ndpointer(dtype=c_int, ndim=1, flags=('C_CONTIGUOUS',)),
                c_int,
                ]

        elif attr.startswith('cint1e') and not attr.endswith('optimizer'):
            cfunc.argtypes = [
                # buf
                ndpointer(dtype=c_double, ndim=2, flags=('F_CONTIGUOUS', 'WRITEABLE')),
                # shls
                ndpointer(dtype=c_int, ndim=1, flags=('C_CONTIGUOUS',)),
                # atm
                ndpointer(dtype=c_int, ndim=2, flags=('C_CONTIGUOUS',)),
                # natm
                c_int,
                # bas
                ndpointer(dtype=c_int, ndim=2, flags=('C_CONTIGUOUS',)),
                # nbas
                c_int,
                # env
                ndpointer(dtype=c_double, ndim=1, flags=('C_CONTIGUOUS',)),
                # opt (not used; put ``None`` as this argument)
                c_void_p,
                ]
            cfunc.restype = c_int

        elif attr.startswith('cint2e') and not attr.endswith('optimizer'):
            cfunc.argtypes = [
                # buf
                ndpointer(dtype=c_double, ndim=4, flags=('F_CONTIGUOUS', 'WRITEABLE')),
                # shls
                ndpointer(dtype=c_int, ndim=1, flags=('C_CONTIGUOUS',)),
                # atm
                ndpointer(dtype=c_int, ndim=2, flags=('C_CONTIGUOUS',)),
                # natm
                c_int,
                # bas
                ndpointer(dtype=c_int, ndim=2, flags=('C_CONTIGUOUS',)),
                # nbas
                c_int,
                # env
                ndpointer(dtype=c_double, ndim=1, flags=('C_CONTIGUOUS',)),
                # opt (not used; put ``None`` as this argument)
                c_void_p,
                ]
            cfunc.restype = c_int

        else:
            raise NotImplementedError('there is no ``gbasis`` API for this function')

        return cfunc


libcint = LibCInt()


# Bind API

CINTlen_cart = libcint.CINTlen_cart
CINTlen_spinor = libcint.CINTlen_spinor

CINTcgtos_cart = libcint.CINTcgtos_cart
CINTcgtos_spheric = libcint.CINTcgtos_spheric
CINTcgtos_spinor = libcint.CINTcgtos_spinor
CINTcgto_cart = libcint.CINTcgto_cart
CINTcgto_spheric = libcint.CINTcgto_spheric
CINTcgto_spinor = libcint.CINTcgto_spinor

CINTtot_pgto_spheric = libcint.CINTtot_pgto_spheric
CINTtot_pgto_spinor = libcint.CINTtot_pgto_spinor

CINTtot_cgto_cart = libcint.CINTtot_cgto_cart
CINTtot_cgto_spheric = libcint.CINTtot_cgto_spheric
CINTtot_cgto_spinor = libcint.CINTtot_cgto_spinor

CINTshells_cart_offset = libcint.CINTshells_cart_offset
CINTshells_spheric_offset = libcint.CINTshells_spheric_offset
CINTshells_spinor_offset = libcint.CINTshells_spinor_offset


# Bind integral functions

cint1e_ovlp_cart = libcint.cint1e_ovlp_cart
cint1e_ovlp_sph = libcint.cint1e_ovlp_sph
cint1e_ovlp = libcint.cint1e_ovlp

cint1e_nuc_cart = libcint.cint1e_nuc_cart
cint1e_nuc_sph = libcint.cint1e_nuc_sph
cint1e_nuc = libcint.cint1e_nuc

cint1e_kin_cart = libcint.cint1e_kin_cart
cint1e_kin_sph = libcint.cint1e_kin_sph
cint1e_kin = libcint.cint1e_kin

cint1e_ia01p_cart = libcint.cint1e_ia01p_cart
cint1e_ia01p_sph = libcint.cint1e_ia01p_sph
cint1e_ia01p = libcint.cint1e_ia01p

# ...and so on... (see cint_funcs.h for list of valid integral functions)
