"""Derivative of a Gaussian Contraction."""
from gbasis.contractions import ContractedCartesianGaussians
import numpy as np
from scipy.special import comb, eval_hermite, perm


# TODO: in the case of generalized Cartesian contraction where multiple shells have the same sets of
# exponents but different sets of primitive coefficients, it will be helpful to vectorize the
# `prim_coeffs` also.
# FIXME: name is pretty bad
# TODO: vectorize for multiple orders? Caching instead?
def _eval_deriv_contractions(coords, orders, center, angmom_comps, alphas, prim_coeffs, norm):
    """Return the evaluation of the derivative of a Cartesian contraction.

    Parameters
    ----------
    coords : np.ndarray(N, 3)
        Point in space where the derivative of the Gaussian primitive is evaluated.
        Coordinates must be given as a two dimensional array, even if one coordinate is given.
    orders : np.ndarray(3,)
        Orders of the derivative.
        Negative orders are treated as zero orders.
    center : np.ndarray(3,)
        Center of the Gaussian primitive.
    angmom_comps : np.ndarray(L, 3)
        Component of the angular momentum that corresponds to this dimension.
        Angular momentum components must be given as a two dimensional array, even if only one
        is given.
    alphas : np.ndarray(K,)
        Values of the (square root of the) precisions of the primitives.
    prim_coeffs : {np.ndarray(K,M), np.ndarray(K,)}
        Contraction coefficients of the primitives.
        If the coefficients correspond to generalized contractions (i.e. two-dimensional array),
        then the first index corresponds to the primitive and the second index corresponds to the
        contraction (with the same exponents and angular momentum).
        If the coefficients correspond to segmented contractions (i.e. one-dimensional array), then
        the first index corresponds to the primitive.
    norm : np.ndarray(L, K)
        Normalization constants for the primitives in each contraction.

    Returns
    -------
    derivative : {np.ndarray(M, L, N), np.ndarray(L, N)}
        Evaluation of the derivative at each given coordinate.
        If the given coefficients is a two-dimensional array (i.e. generalized contracitons), then a
        three dimensional array is returned, where the first index corresponds to the contraction,
        second index corrresponds to the angular momentum vector, and the third index corresponds to
        the coordinate for the evaluation
        If the given coefficients is a one-dimensional array (i.e. segmented contracitons), then a
        two dimensional array is returned, where the first index corrresponds to the angular
        momentum vector, and the second index corresponds to the coordinate for the evaluation

    Notes
    -----
    The input is not checked. This means that you must provide the parameters as they are specified
    in the docstring. They must all be numpy arrays with the **correct shape**.

    Pople style basis sets are not supported. If multiple angular momentum vectors (with different
    angular momentum) and multiple contraction coefficients are provided, it is **not assumed** that
    the angular momentum vector should be paired up with the contraction coefficients. In fact, each
    angular momentum vector will create multiple contractions according to the given coefficients.

    Multiple shapes of `prim_coeffs` are supported at the expense of concise API. For example, we
    assumed that the `prim_coeffs` is always 2-dimensional, such that the coefficients for a
    segmented contraction will have the shape `(K, 1)`. However, it takes a little more time to
    evaluate a two-dimensional array over a one-dimensional array, even if their size is the same.
    We support different shapes of `prim_coeffs` to keep this little bit of performance.

    """
    # pylint: disable=R0914
    # NOTE: following convention will be used to organize the axis of the multidimensional arrays
    # axis 0 = index for term in hermite polynomial (size: min(K, n)) where n is the order in given
    # dimension
    # axis 1 = index for primitive (size: K)
    # axis 2 = index for dimension (x, y, z) of coordinate (size: 3)
    # axis 3 = index for angular momentum vector (size: L)
    # axis 4 = index for coordinate (out of a grid) (size: N)
    # adjust the axis
    coords = coords.T[np.newaxis, np.newaxis, :, np.newaxis, :]
    # NOTE: if `coord` is two dimensional (3, N), then coords has shape (1, 1, 3, 1, N). If it is
    # one dimensional (3,), then coords has shape (1, 1, 3, 1)
    # NOTE: `order` is still assumed to be a one dimensional
    center = center[np.newaxis, np.newaxis, :, np.newaxis, np.newaxis]
    angmom_comps = angmom_comps.T[np.newaxis, np.newaxis, :, :, np.newaxis]
    # NOTE: if `angmom_comps` is two-dimensional (3, L), has shape (1, 1, 3, L). If it is one
    # dimensional (3, ) then it has shape (1, 1, 3)
    alphas = alphas[np.newaxis, :, np.newaxis, np.newaxis, np.newaxis]
    # NOTE: `prim_coeffs` will be used as a 1D array

    # useful variables
    rel_coords = coords - center
    gauss = np.exp(-alphas * rel_coords ** 2)

    # zeroth order (i.e. no derivatization)
    indices_noderiv = orders <= 0
    zero_rel_coords, zero_angmom_comps, zero_gauss = (
        rel_coords[:, :, indices_noderiv],
        angmom_comps[:, :, indices_noderiv],
        gauss[:, :, indices_noderiv],
    )
    zeroth_part = np.prod(zero_rel_coords ** zero_angmom_comps * zero_gauss, axis=(0, 2))
    # NOTE: `zeroth_part` now has axis 0 for primitives, axis 1 for angular momentum vector, and
    # axis 2 for coordinate

    deriv_part = 1
    nonzero_rel_coords, nonzero_orders, nonzero_angmom_comps, nonzero_gauss = (
        rel_coords[:, :, ~indices_noderiv],
        orders[~indices_noderiv],
        angmom_comps[:, :, ~indices_noderiv],
        gauss[:, :, ~indices_noderiv],
    )
    nonzero_orders = nonzero_orders[np.newaxis, np.newaxis, :, np.newaxis, np.newaxis]

    # derivatization part
    if nonzero_orders.size != 0:
        # General approach: compute the whole coefficents, zero out the irrelevant parts
        # NOTE: The following step assumes that there is only one set (nx, ny, nz) of derivatization
        # orders i.e. we assume that only one axis (axis 2) of `nonzero_orders` has a dimension
        # greater than 1
        indices_herm = np.arange(np.max(nonzero_orders) + 1)[:, None, None, None, None]
        # get indices that are used as powers of the appropriate terms in the derivative
        # NOTE: the negative indices must be turned into zeros (even though they are turned into
        # zeros later anyways) because these terms are sometimes zeros (and negative power is
        # undefined).
        indices_angmom = nonzero_angmom_comps - nonzero_orders + indices_herm
        indices_angmom[indices_angmom < 0] = 0
        # get coefficients for all entries
        coeffs = (
            comb(nonzero_orders, indices_herm)
            * perm(nonzero_angmom_comps, nonzero_orders - indices_herm)
            * (-alphas ** 0.5) ** indices_herm
            * nonzero_rel_coords ** indices_angmom
        )
        # zero out the appropriate terms
        indices_zero = np.where(indices_herm < np.maximum(0, nonzero_orders - nonzero_angmom_comps))
        coeffs[indices_zero[0], :, indices_zero[2], indices_zero[3]] = 0
        indices_zero = np.where(nonzero_orders < indices_herm)
        coeffs[indices_zero[0], :, indices_zero[2]] = 0
        # compute
        # TODO: I don't know if the scipy.special.eval_hermite uses some smart vectorizing/caching
        # to evaluate multiple orders at the same time. Creating/finding a better function for
        # evaluating the hermite polynomial at different orders (in sequence) may be nice in the
        # future.
        hermite = np.sum(
            coeffs * eval_hermite(indices_herm, alphas ** 0.5 * nonzero_rel_coords), axis=0
        )
        hermite = np.prod(hermite, axis=1)

        # NOTE: `hermite` now has axis 0 for primitives, 1 for angular momentum vector, and axis 2
        # for coordinates
        deriv_part = np.prod(nonzero_gauss, axis=(0, 2)) * hermite

    norm = norm.T[:, :, np.newaxis]
    return np.tensordot(prim_coeffs, norm * zeroth_part * deriv_part, (0, 0))


def eval_deriv_shell(*, coords, orders, shell):
    """Return the derivatives of a set of Cartesian contractions evaluated at the given coordinates.

    Parameters
    ----------
    coords : np.ndarray(N, 3)
        Point in space where the derivative of the Gaussian primitive is evaluated.
    orders : np.ndarray(3,)
        Orders of the derivative.
        Negative orders are treated as zero orders.
    shell : ContractedCartesianGaussians
        Set of contracted Cartesian Gaussians with the same angular momentum.

    Returns
    -------
    derivative : np.ndarray(L, N)
        Evaluation of the derivative.
        :math:`L` is the number of contractions associated with the given `shell`.

    Raises
    ------
    TypeError
        If the arguments are given as positional arguments.
        If coords is not a numpy array.
        If orders is not a numpy array.
        If shell is not a ContractedCartesianGaussians.
    ValueError
        If coords is not a two-dimensional numpy array with 3 columns.
        If orders is not a one-dimensional numpy array with 3 entries.

    Notes
    -----
    When calling this function, the arguments must be given via keywords and not positional
    arguments. This feature is used to catch problems that arise due to a change in API.

    """
    if not isinstance(coords, np.ndarray):
        raise TypeError("Coordinates must be provided as a numpy array.")
    if coords.ndim == 1 and coords.size == 3:
        coords = coords.reshape(1, 3)
    if not (coords.ndim == 2 and coords.shape[1] == 3):
        raise ValueError(
            "Coordinates must be provided as a two-dimensional numpy array with 3 columns."
        )
    if not isinstance(orders, np.ndarray):
        raise TypeError("Orders of the derivatives must be a numpy array")
    if not orders.shape == (3,):
        raise ValueError(
            "Orders of derivatives must be given as a one-dimensional numpy array with three "
            "entries"
        )
    if not isinstance(shell, ContractedCartesianGaussians):
        raise TypeError('Each "shell" must be a ContractedCartesianGaussians instance.')

    alphas = shell.exps
    prim_coeffs = shell.coeffs
    angmom_comps = shell.angmom_components
    center = shell.coord
    norm = shell.norm
    return _eval_deriv_contractions(coords, orders, center, angmom_comps, alphas, prim_coeffs, norm)


def eval_shell(*, coords, shell):
    """Return the set of Cartesian contractions evaluated at the given coordinates.

    Parameters
    ----------
    coords : np.ndarray(N, 3)
        Point in space where the Gaussian primitive is evaluated.
    shell : ContractedCartesianGaussians
        Set of contracted Cartesian Gaussians with the same angular momentum.

    Returns
    -------
    derivative : np.ndarray(L, N)
        Evaluation of the (zeroth-order) derivative.
        :math:`L` is the number of contractions associated with the given `shell`.

    Raises
    ------
    TypeError
        If the arguments are given as positional arguments.
        If coords is not a numpy array.
        If shell is not a ContractedCartesianGaussians.
    ValueError
        If coords is not a two-dimensional numpy array with 3 columns.

    Notes
    -----
    When calling this function, the arguments must be given via keywords and not positional
    arguments. This feature is used to catch problems that arise due to a change in API.

    """
    return eval_deriv_shell(coords=coords, orders=np.zeros(shell.coord.shape), shell=shell)  # nosec
