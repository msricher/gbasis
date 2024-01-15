"""Test gbasis.integrals.libcint."""
from gbasis.contractions import GeneralizedContractionShell
from gbasis.integrals._moment_int import _compute_multipole_moment_integrals
from gbasis.integrals.overlap import Overlap, overlap_integral
from gbasis.integrals.libcint import CBasis
from gbasis.parsers import make_contractions, parse_nwchem
import numpy as np
import pytest
from scipy.special import factorial2
from utils import find_datafile, HortonContractions


# def test_overlap_construct_array_contraction():
#     """Test gbasis.integrals.overlap.Overlap.construct_array_contraction."""
#     test_one = GeneralizedContractionShell(
#         1, np.array([0.5, 1, 1.5]), np.array([1.0, 2.0]), np.array([0.1, 0.01])
#     )
#     test_two = GeneralizedContractionShell(
#         2, np.array([1.5, 2, 3]), np.array([3.0, 4.0]), np.array([0.2, 0.02])
#     )
#     answer = np.array(
#         [
#             [
#                 _compute_multipole_moment_integrals(
#                     np.array([0, 0, 0]),
#                     np.array([[0, 0, 0]]),
#                     np.array([0.5, 1, 1.5]),
#                     np.array([angmom_comp_one]),
#                     np.array([0.1, 0.01]),
#                     np.array([[1], [2]]),
#                     np.array(
#                         [
#                             [
#                                 (2 * 0.1 / np.pi) ** (3 / 4)
#                                 * (4 * 0.1) ** (1 / 2)
#                                 / np.sqrt(np.prod(factorial2(2 * angmom_comp_one - 1))),
#                                 (2 * 0.01 / np.pi) ** (3 / 4)
#                                 * (4 * 0.01) ** (1 / 2)
#                                 / np.sqrt(np.prod(factorial2(2 * angmom_comp_one - 1))),
#                             ]
#                         ]
#                     ),
#                     np.array([1.5, 2, 3]),
#                     np.array([angmom_comp_two]),
#                     np.array([0.2, 0.02]),
#                     np.array([[3], [4]]),
#                     np.array(
#                         [
#                             [
#                                 (2 * 0.2 / np.pi) ** (3 / 4)
#                                 * (4 * 0.2) ** (2 / 2)
#                                 / np.sqrt(np.prod(factorial2(2 * angmom_comp_two - 1))),
#                                 (2 * 0.02 / np.pi) ** (3 / 4)
#                                 * (4 * 0.02) ** (2 / 2)
#                                 / np.sqrt(np.prod(factorial2(2 * angmom_comp_two - 1))),
#                             ]
#                         ]
#                     ),
#                 )
#                 for angmom_comp_two in test_two.angmom_components_cart
#             ]
#             for angmom_comp_one in test_one.angmom_components_cart
#         ]
#     )
#     assert np.allclose(
#         np.squeeze(Overlap.construct_array_contraction(test_one, test_two)), np.squeeze(answer)
#     )
#
#     with pytest.raises(TypeError):
#         Overlap.construct_array_contraction(test_one, None)
#     with pytest.raises(TypeError):
#         Overlap.construct_array_contraction(None, test_two)
#
#
# def test_overlap_cartesian():
#     """Test gbasis.integrals.overlap.overlap_cartesian."""
#     basis_dict = parse_nwchem(find_datafile("data_sto6g.nwchem"))
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(
#         overlap_obj.construct_array_cartesian(), overlap_integral(basis, coord_type="cartesian")
#     )
#
#
# def test_overlap_spherical():
#     """Test gbasis.integrals.overlap.overlap_spherical."""
#     basis_dict = parse_nwchem(find_datafile("data_sto6g.nwchem"))
#
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(
#         overlap_obj.construct_array_spherical(), overlap_integral(basis, coord_type="spherical")
#     )
#
#
# def test_overlap_mix():
#     """Test gbasis.integrals.overlap.overlap_mix."""
#     basis_dict = parse_nwchem(find_datafile("data_sto6g.nwchem"))
#
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(
#         overlap_obj.construct_array_mix(["spherical"] * 8),
#         overlap_integral(basis, coord_type=["spherical"] * 8),
#     )
#
#
# def test_overlap_lincomb():
#     """Test gbasis.integrals.overlap.overlap_lincomb."""
#     basis_dict = parse_nwchem(find_datafile("data_sto6g.nwchem"))
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     transform = np.random.rand(14, 18)
#     assert np.allclose(
#         overlap_obj.construct_array_lincomb(transform, "spherical"),
#         overlap_integral(basis, transform=transform, coord_type="spherical"),
#     )
#
#
# def test_overlap_cartesian_norm_anorcc():
#     """Test the norm of gbasis.integrals.overlap_cartesian on the ANO-RCC basis set.
#
#     The contraction coefficients in ANO-RCC is such that the cartesian contractions are normalized.
#
#     """
#     basis_dict = parse_nwchem(find_datafile("data_anorcc.nwchem"))
#
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(np.diag(overlap_obj.construct_array_cartesian()), 1)
#
#
# def test_overlap_spherical_norm_sto6g():
#     """Test the norm of gbasis.integrals.overlap_spherical on the STO-6G basis set.
#
#     The contraction coefficients in STO-6G is such that the spherical contractions are not
#     normalized to past 3rd decimal places.
#
#     """
#     basis_dict = parse_nwchem(find_datafile("data_sto6g.nwchem"))
#
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(np.diag(overlap_obj.construct_array_spherical()), 1)
#
#
# def test_overlap_spherical_norm_anorcc():
#     """Test the norm of gbasis.integrals.overlap_spherical on the ANO-RCC basis set.
#
#     The contraction coefficients in ANO-RCC is such that the Cartesian contractions are normalized.
#
#     """
#     basis_dict = parse_nwchem(find_datafile("data_anorcc.nwchem"))
#
#     basis = make_contractions(basis_dict, ["C"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(np.diag(overlap_obj.construct_array_cartesian()), 1)
#
#     basis = make_contractions(basis_dict, ["Xe"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(np.diag(overlap_obj.construct_array_cartesian()), 1)
#
#
# def test_overlap_cartesian_norm_sto6g():
#     """Test the norm of gbasis.integrals.overlap_cartesian on the STO-6G basis set.
#
#     The contraction coefficients in STO-6G is such that the Cartesian contractions are not
#     normalized to past 3rd decimal places.
#
#     """
#     basis_dict = parse_nwchem(find_datafile("data_sto6g.nwchem"))
#
#     basis = make_contractions(basis_dict, ["Kr"], np.array([[0, 0, 0]]))
#     overlap_obj = Overlap(basis)
#     assert np.allclose(np.diag(overlap_obj.construct_array_cartesian()), 1)


def test_overlap_horton_anorcc_hhe():
    """Test gbasis.integrals.overlap.overlap_basis_cartesian against HORTON's overlap matrix.

    The test case is diatomic with H and He separated by 0.8 angstroms with basis set ANO-RCC.

    """
    basis_dict = parse_nwchem(find_datafile("data_anorcc.nwchem"))
    # NOTE: used HORTON's conversion factor for angstroms to bohr
    basis = make_contractions(
        basis_dict, ["H", "He"], np.array([[0, 0, 0], [0.8 * 1.0 / 0.5291772083, 0, 0]])
    )
    basis = [HortonContractions(i.angmom, i.coord, i.coeffs, i.exps) for i in basis]

    horton_overlap = np.load(find_datafile("data_horton_hhe_cart_overlap.npy"))
    assert np.allclose(CBasis(basis, coord_type="cartesian").olp(), horton_overlap)


def test_overlap_horton_anorcc_bec():
    """Test gbasis.integrals.overlap.overlap_cartesian against HORTON's overlap matrix.

    The test case is diatomic with Be and C separated by 1.0 angstroms with basis set ANO-RCC.

    """
    basis_dict = parse_nwchem(find_datafile("data_anorcc.nwchem"))
    # NOTE: used HORTON's conversion factor for angstroms to bohr
    basis = make_contractions(
        basis_dict, ["Be", "C"], np.array([[0, 0, 0], [1.0 * 1.0 / 0.5291772083, 0, 0]])
    )
    basis = [HortonContractions(i.angmom, i.coord, i.coeffs, i.exps) for i in basis]

    horton_overlap = np.load(find_datafile("data_horton_bec_cart_overlap.npy"))
    assert np.allclose(CBasis(basis, coord_type="cartesian").olp(), horton_overlap)
