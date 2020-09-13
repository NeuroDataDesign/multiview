"""Group Principal Component Analysis."""
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
# Authors: Pierre Ablin, Hugo Richard

import numpy as np
from sklearn.decomposition import PCA
from sklearn.utils.validation import check_is_fitted


from ..utils.utils import check_Xs
from .base import BaseDecomposer


class GroupPCA(BaseDecomposer):
    r"""Group Principal Component Analysis.

    As an optional preprocessing, each dataset in `Xs` is reduced with
    usual PCA. Then, datasets are concatenated in the features direction,
    and a PCA is performed on this matrix, yielding a single output dataset.

    Parameters
    ----------
    n_components : int, optional
        Number of components to extract. If None, n_components is set to
        the minimum number of features in the dataset.

    n_individual_components : int or list of int or 'auto', optional
        The number of individual components to extract as a preprocessing.
        If None, no preprocessing is applied. If an `int`, each dataset
        is reduced to this dimension. If a list, the dataset `i` is
        reduced to the dimension `n_individual_components[i]`.
        If `'auto'`, set to the minimum between n_components and the
        smallest number of features in each dataset.

    copy : bool, default=True
        If False, data passed to fit are overwritten and running
        fit(X).transform(X) will not yield the expected results,
        use fit_transform(X) instead.

    prewhiten : bool, optional (default False)
        Whether the data should be whitened after the original preprocessing.

    whiten : bool, optional (default False)
        When True (False by default) the `components_` vectors are multiplied
        by the square root of n_samples and then divided by the singular values
        to ensure uncorrelated outputs with unit component-wise variances.
        Whitening will remove some information from the transformed signal
        (the relative variance scales of the components) but can sometime
        improve the predictive accuracy of the downstream estimators by
        making their data respect some hard-wired assumptions.

    random_state : int, RandomState instance, default=None
        Used when ``svd_solver`` == 'arpack' or 'randomized'. Pass an int
        for reproducible results across multiple function calls.

    Attributes
    ----------
    components_ : array, shape (n_components, n_total_features)
        Principal axes in feature space, representing the directions of
        maximum variance in the data. The components are sorted by
        ``explained_variance_``. `n_total_features` is the sum of all
        the number of input features.

    explained_variance_ : array, shape (n_components,)
        The amount of variance explained by each of the selected components.

    explained_variance_ratio_ : array, shape (n_components,)
        Percentage of variance explained by each of the selected components.
        If ``n_components`` is not set then all components are stored and the
        sum of the ratios is equal to 1.0.

    mean_ : array, shape (n_total_features, )
        Per-feature empirical mean, estimated from the training set.

    individual_components_ : list of array
        Individual components for each individual PCA.
        `individual_components_[i]` is an array of shape
        (n_individual_components, n_features) where n_features is the number of
        features in the dataset `i`.

    individual_explained_variance_ : list of array
        Individual explained variance for each individual PCA.
        `individual_explained_variance_[i]` is an array of shape
        (n_individual_components, ).

    individual_explained_variance_ratio_ : list of array
        Individual explained variance ratio for each individual PCA.
        `individual_explained_variance_ratio_[i]` is an array of shape
        (n_individual_components, ) where n_features is the number of
        features in the dataset `i`.

    individual_mean_ : list of array
        Individual mean for each individual PCA.
        `individual_mean_[i]` is an array of shape
        (n_features) where n_features is the number of
        features in the dataset `i`.

    n_components_ : int
        The estimated number of components.

    n_features_ : list of int
        Number of features in each training dataset.

    n_samples_ : int
        Number of samples in the training data.

    n_views_ : int
        Number of views in the training data

    References
    ----------
    .. [#1grouppca] Calhoun, Vince, et al. "A method for making group
                    inferences from functional MRI data using independent
                    component analysis."
                    Human brain mapping 14.3 (2001): 140-151.

    Examples
    --------
    >>> from mvlearn.datasets import load_UCImultifeature
    >>> from mvlearn.decomposition import GroupPCA
    >>> Xs, _ = load_UCImultifeature()
    >>> pca = GroupPCA(n_components=3)
    >>> Xs_transformed = pca.fit_transform(Xs)
    >>> print(Xs_transformed.shape)
    (2000, 3)
    """

    def __init__(
        self,
        n_components=None,
        n_individual_components="auto",
        copy=True,
        prewhiten=False,
        whiten=False,
        random_state=None,
    ):
        self.n_components = n_components
        self.n_individual_components = n_individual_components
        self.copy = copy
        self.prewhiten = prewhiten
        self.whiten = whiten
        self.random_state = random_state

    def fit_transform(self, Xs, y=None):
        """Fit  to the data and transform the data.


        This merges datasets together and reduces the dimensionality.

        Parameters
        ----------
        Xs : list of array-likes or numpy.ndarray
             - Xs length: n_views
             - Xs[i] shape: (n_samples, n_features_i)
        y : array, shape (n_samples,), optional

        Returns
        -------
        X_transformed : array of shape (n_samples, n_components)
            The transformed data
        """
        Xs = check_Xs(Xs, copy=self.copy)
        n_features = [X.shape[1] for X in Xs]
        self.n_views_ = len(Xs)
        self.n_features_ = n_features
        self.n_samples_ = Xs[0].shape[0]

        if self.n_components is None:
            self.n_components_ = min(n_features)
        else:
            self.n_components_ = self.n_components
        if self.n_individual_components == "auto":
            self.n_individual_components_ = min(
                self.n_components_, min(n_features)
            )
        else:
            self.n_individual_components_ = self.n_individual_components
        if self.n_individual_components_ is None and self.prewhiten:
            # Still need to whiten data
            self.n_individual_components_ = self.n_features_
        self.individual_projection_ = self.n_individual_components_ is not None

        if self.individual_projection_:
            if type(self.n_individual_components_) == int:
                one_dimension = True
            else:
                one_dimension = False
            self.individual_components_ = []
            self.individual_explained_variance_ = []
            self.individual_explained_variance_ratio_ = []
            self.individual_mean_ = []
            for i, X in enumerate(Xs):
                if one_dimension:
                    dimension = self.n_individual_components_
                else:
                    dimension = self.n_individual_components_[i]
                pca = PCA(
                    dimension,
                    whiten=self.prewhiten,
                    random_state=self.random_state,
                )
                Xs[i] = pca.fit_transform(X)
                self.individual_components_.append(pca.components_)
                self.individual_explained_variance_ratio_.append(
                    pca.explained_variance_ratio_
                )
                self.individual_explained_variance_.append(
                    pca.explained_variance_
                )
                self.individual_mean_.append(pca.mean_)
        X_stack = np.hstack(Xs)
        pca = PCA(self.n_components_, whiten=self.whiten)
        output = pca.fit_transform(X_stack)
        self.components_ = pca.components_
        self.explained_variance_ = pca.explained_variance_
        self.mean_ = pca.mean_
        self.explained_variance_ratio_ = pca.explained_variance_ratio_
        return output

    def fit(self, Xs, y=None):
        r"""Fit the model with Xs.

        Parameters
        ----------
        Xs: list of array-likes
            - Xs shape: (n_views,)
            - Xs[i] shape: (n_samples, n_features_i)

        y : None
            Ignored variable.
        Returns
        -------
        self : object
            Returns the instance itself.
        """
        self.fit_transform(Xs, y)
        return self

    def transform(self, Xs, y=None):
        r"""
        Apply groupPCA to Xs.

        Xs is projected on the principal components learned
        in the training set.

        Parameters
        ----------
        Xs: list of array-likes
            - Xs shape: (n_views,)
            - Xs[i] shape: (n_samples, n_features_i)
        y : array, shape (n_samples,), optional

        Returns
        -------
        X_transformed : array of shape (n_samples, n_components)
            The transformed data
        """
        check_is_fitted(self)
        Xs = check_Xs(Xs, copy=self.copy)

        if self.individual_projection_:
            for i, (X, mean, components_, explained_variance_) in enumerate(
                zip(
                    Xs,
                    self.individual_mean_,
                    self.individual_components_,
                    self.individual_explained_variance_,
                )
            ):
                X = X - mean
                X_transformed = np.dot(X, components_.T)
                if self.prewhiten:
                    X_transformed /= np.sqrt(explained_variance_)
                Xs[i] = X_transformed
        X_stack = np.hstack(Xs) - self.mean_
        X_transformed = np.dot(X_stack, self.components_.T)
        if self.whiten:
            X_transformed /= np.sqrt(self.explained_variance_)
        return X_transformed

    def inverse_transform(self, X_transformed):
        r"""
        Recover multiview data from transformed data.

        Returns an array Xs such that the transform of Xs would be
        X_transformed

        Parameters
        ----------
        X_transformed : array of shape (n_samples, n_components)
            The dataset corresponding to transformed data

        Returns
        -------
        Xs : list of arrays
            The recovered individual datasets
        """
        check_is_fitted(self)

        # Inverse stacked PCA
        if self.whiten:
            X_t = X_transformed * np.sqrt(self.explained_variance_)
        else:
            X_t = X_transformed
        X_stack = np.dot(X_t, self.components_)
        X_stack = X_stack + self.mean_

        if self.individual_projection_:
            Xs = []
            cur_p = 0
            for (mean, components_, explained_variance_) in zip(
                self.individual_mean_,
                self.individual_components_,
                self.individual_explained_variance_,
            ):
                n_features_i = components_.shape[0]
                sl = slice(cur_p, cur_p + n_features_i)
                X_i = X_stack[:, sl]
                if self.prewhiten:
                    X_i *= np.sqrt(explained_variance_)
                X_i = np.dot(X_i, components_)
                X_i = X_i + mean
                Xs.append(X_i)
                cur_p += n_features_i
        else:
            Xs = np.split(X_stack, np.cumsum(self.n_features_)[:-1], axis=1)
        return Xs
