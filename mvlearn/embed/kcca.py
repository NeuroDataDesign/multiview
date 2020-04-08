# Copyright 2019 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Adopted from Steven Van Vaerenbergh's MATLAB Package 'KMBOX'
# https://github.com/steven2358/kmbox

from .base import BaseEmbed
from ..utils.utils import check_Xs

import numpy as np
from scipy import linalg
from sklearn.metrics.pairwise import euclidean_distances


class KCCA(BaseEmbed):
    r"""
    The kernel canonical correlation analysis (KCCA) is a method
    that generalizes the classical linear canonical correlation
    analysis (CCA) to nonlinear setting.  It allows us to depict the
    nonlinear relation of two sets of variables and enables
    applications of classical multivariate data analysis
    originally constrained to linearity relation (CCA).

    Parameters
    ----------
    n_components : int, default = 10
                   Number of canonical dimensions to keep
    ktype : string, default = 'linear'
            Type of kernel
        - value can be 'linear', 'gaussian' or 'poly'
    degree : float, default = 2.0
             Degree of Polynomial kernel
    constant : float, default = 1.0
             Balances impact of lower-degree terms in Polynomial kernel
    sigma : float, default = 1.0
            Standard deviation of Gaussian kernel
    reg : float, default = 0.1
          Regularization parameter
    decomp : string, default = 'full'
             Decomposition type
        - value can be only be 'full'
    method : string, default = 'kettenring-like'
             Decomposition method
        - value can be only be 'kettenring-like'

    Notes
    -----
    This class implements kernel canonical correlation analysis
    as described in [#1KCCA]_ and [#2KCCA]_.

    Traditional CCA aims to find useful projections of the
    high- dimensional variable sets onto the compact
    linear representations, the canonical components (components_).

    Each resulting canonical variate is computed from
    the weighted sum of every original variable indicated
    by the canonical weights (weights_).

    The canonical correlation quantifies the linear
    correspondence between the two views of data
    based on Pearson’s correlation between their
    canonical components.

    Canonical correlation can be seen as a metric of
    successful joint information reduction between two views
    and, therefore, routinely serves as a performance measure for CCA.

    CCA may not extract useful descriptors of the data because of
    its linearity. kCCA offers an alternative solution by first
    projecting the data onto a higher dimensional feature space.

    .. math::
        \phi: \mathbf{x} = (x_1,...,x_m) \mapsto
        \phi(\mathbf{x}) = (\phi(x_1),...,\phi(x_N)),
        (m < N)

    before performing CCA in the new feature space.

    Kernels are methods of implicitly mapping data into a higher
    dimensional feature space, a method known as the kernel trick.
    A kernel function K, such that for all :math:`\mathbf{x},
    \mathbf{z} \in X`,

    .. math::
        K(\mathbf{x}, \mathbf{z}) = \langle\phi(\mathbf{x})
        \cdot \phi(\mathbf{z})\rangle,

    where :math:`\phi` is a mapping from X to feature space F.

    The directions :math:`\mathbf{w_x}` and :math:`\mathbf{w_y}`
    (of length N) can be rewritten as the projection of the data
    onto the direction :math:`\alpha` and :math:`\alpha`
    (of length m):

    .. math::
        \mathbf{w_x} = X'\alpha
        \mathbf{w_y} = Y'\beta

    Letting :math:`K_x = XX'` and :math:`K_x = XX'` be the kernel
    matrices and adding a regularization term (:math:`\kappa`)
    to prevent overfitting, we are effectively solving for:

    .. math::
        \rho = \underset{\alpha,\beta}{\text{max}}
        \frac{\alpha'K_xK_y\beta}
        {\sqrt{(\alpha'K_x^2\alpha+\kappa\alpha'K_x\alpha)
        \cdot (\beta'K_y^2\beta + \kappa\beta'K_y\beta)}}


    References
    ----------
    .. [#1KCCA] D. R. Hardoon, S. Szedmak and J. Shawe-Taylor,
            "Canonical Correlation Analysis: An Overview with
            Application to Learning Methods", Neural Computation,
            Volume 16 (12), Pages 2639--2664, 2004.
    .. [#2KCCA] J. R. Kettenring, “Canonical analysis of several sets of
            variables,”Biometrika, vol.58, no.3, pp.433–451,1971.


    Example
    -------
    >>> import numpy as np
    >>> from scipy import stats
    >>> from mvlearn.embed.kcca import KCCA
    >>> np.random.seed(1)
    >>> # Define two latent variables
    >>> N = 100
    >>> latvar1 = np.random.randn(N, )
    >>> latvar2 = np.random.randn(N, )
    >>> # Define independent components for each dataset
    >>> indep1 = np.random.randn(N, 4)
    >>> indep2 = np.random.randn(N, 5)
    >>> x = 0.25*indep1 + 0.75*np.vstack((latvar1, latvar2,
    ...                                   latvar1, latvar2)).T
    >>> y = 0.25*indep2 + 0.75*np.vstack((latvar1, latvar2,
    ...                                   latvar1, latvar2, latvar1)).T
    >>> Xs = [x, y]
    >>> Xs_train = [Xs[0][:20], Xs[1][:20]]
    >>> Xs_test = [Xs[0][20:], Xs[1][20:]]
    >>> kcca_l = KCCA(ktype ="linear", n_components = 4)
    >>> a = kcca_l.fit(Xs_train)
    >>> linearkcca = kcca_l.transform(Xs_test)
    >>> (r1, _) = stats.pearsonr(linearkcca[0][:,0], linearkcca[1][:,0])
    >>> (r2, _) = stats.pearsonr(linearkcca[0][:,1], linearkcca[1][:,1])
    >>> (r3, _) = stats.pearsonr(linearkcca[0][:,2], linearkcca[1][:,2])
    >>> (r4, _) = stats.pearsonr(linearkcca[0][:,3], linearkcca[1][:,3])
    >>> #Below are the canonical correlation for the four components:
    >>> print(round(r1, 2), round(r2, 2), round(r3, 2), round(r4,2))
    0.85 0.94 -0.25 -0.03


    """

    def __init__(
        self,
        n_components=2,
        ktype='linear',
        constant=0.1,
        sigma=1.0,
        degree=2.0,
        reg=0.1,
        decomp='full',
        method='kettenring-like',
    ):
        self.n_components = n_components
        self.ktype = ktype
        self.constant = constant
        self.sigma = sigma
        self.degree = degree
        self.reg = reg
        self.decomp = decomp
        self.method = method

        # Error Handling
        if self.n_components < 0 or not type(self.n_components) == int:
            raise ValueError("n_components must be a positive integer")
        if ((self.ktype != "linear") and (self.ktype != "poly")
                and (self.ktype != "gaussian")):
            raise ValueError("ktype must be 'linear', 'gaussian', or 'poly'.")
        if self.sigma < 0 or not (type(self.sigma) == float
                                  or type(self.sigma) == int):
            raise ValueError("sigma must be positive int/float")
        if not (type(self.degree) == float or type(self.sigma) == int):
            raise ValueError("degree must be int/float")
        if self.reg < 0 or self.reg > 1 or not type(self.reg) == float:
            raise ValueError("reg must be positive float")
        if self.constant < 0 or not (type(self.constant) == float
                                     or type(self.constant) == int):
            raise ValueError("constant must be a positive integer")

    def fit(self, Xs, y=None):
        r"""
        Creates kcca mapping by determining
        canonical weghts from Xs.

        Parameters
        ----------
        Xs : list of array-likes or numpy.ndarray
             - Xs length: n_views
             - Xs[i] shape: (n_samples, n_features_i)
            The data for kcca to fit to.
            Each sample will receive its own embedding.

        Returns
        -------
        self : returns an instance of self

        """
        Xs = check_Xs(Xs, multiview=True)

        self.X = _center_norm(Xs[0])
        self.Y = _center_norm(Xs[1])

        N = len(self.X)

        if self.decomp == "full":
            Kx = _make_kernel(self.X, self.X, self.ktype, self.constant,
                              self.degree, self.sigma)
            Ky = _make_kernel(self.Y, self.Y, self.ktype, self.constant,
                              self.degree, self.sigma)

            Id = np.eye(N)
            Z = np.zeros((N, N))

            # Method: Kettenring-like generalizable formulation
            if self.method == "kettenring-like":
                R = 0.5*np.r_[np.c_[Kx, Ky], np.c_[Kx, Ky]]
                D = np.r_[np.c_[Kx+self.reg*Id, Z], np.c_[Z, Ky+self.reg*Id]]

        # Solve eigenvalue problem
        betas, alphas = linalg.eig(R, D)

        # Top eigenvalues
        ind = np.argsort(betas)[::-1][:self.n_components]

        # Extract relevant coordinates and normalize to unit length
        weight1 = alphas[:N, ind]
        weight2 = alphas[N:, ind]

        weight1 /= np.linalg.norm(weight1, axis=0)
        weight2 /= np.linalg.norm(weight2, axis=0)

        self.weights_ = np.real([weight1, weight2])

        return self

    def transform(self, Xs):
        r"""
        Uses KCCA weights to transform Xs into canonical components
        and calculates correlations.

        Parameters
        ----------
        Xs : list of array-likes or numpy.ndarray
             - Xs length: 2
             - Xs[i] shape: (n_samples, n_features_i)
            The data for kcca to fit to.
            Each sample will receive its own embedding.

        weights_ : list of array-likes
                   Canonical weights

        Returns
        -------
        components_ : returns Xs_transformed, a list of numpy.ndarray
             - Xs length: 2
             - Xs[i] shape: (n_samples, n_samples)
        """

        if not hasattr(self, "weights_"):
            raise NameError("kCCA has not been trained.")

        Xs = check_Xs(Xs, multiview=True)

        Kx_transform = _make_kernel(_center_norm(Xs[0]),
                                    _center_norm(self.X),
                                    self.ktype,
                                    self.constant,
                                    self.degree,
                                    self.sigma)
        Ky_transform = _make_kernel(_center_norm(Xs[1]),
                                    _center_norm(self.Y),
                                    self.ktype,
                                    self.constant,
                                    self.degree,
                                    self.sigma)

        weight1 = self.weights_[0]
        weight2 = self.weights_[1]

        comp1 = []
        comp2 = []

        for i in range(weight1.shape[1]):
            comp1.append(Kx_transform@weight1[:, i])
            comp2.append(Ky_transform@weight2[:, i])

        comp1 = np.transpose(np.asarray(comp1))
        comp2 = np.transpose(np.asarray(comp2))

        self.components_ = [comp1, comp2]

        return self.components_


def _center_norm(x):
    x = x - x.mean(0)
    return x


def _make_kernel(X, Y, ktype, constant=0.1, degree=2.0, sigma=1.0):
    Nl = len(X)
    Nr = len(Y)
    N0l = np.eye(Nl) - 1 / Nl * np.ones(Nl)
    N0r = np.eye(Nr) - 1 / Nr * np.ones(Nr)

    # Linear kernel
    if ktype == "linear":
        return N0l @ (X @ Y.T) @ N0r

    # Polynomial kernel
    elif ktype == "poly":
        return N0l @ (X @ Y.T + constant) ** degree @ N0r

    # Gaussian kernel
    elif ktype == "gaussian":
        distmat = euclidean_distances(X, Y, squared=True)

        return N0l @ np.exp(-distmat / (2 * sigma ** 2)) @ N0r
