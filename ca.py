"""Correspondence Analysis (CA)"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn import base
from sklearn import utils

#from . import plot
import util
import svd


class CA(base.BaseEstimator, base.TransformerMixin):

    def __init__(self, n_components=2, n_iter=10, copy=True, check_input=True, random_state=None,
                 engine='auto'):
        self.n_components = n_components
        self.n_iter = n_iter
        self.copy = copy
        self.check_input = check_input
        self.random_state = random_state
        self.engine = engine

    def fit(self, X, y=None):

        # Check input
        if self.check_input:
            utils.check_array(X)

        # Check all values are positive
        if (X < 0).any().any():
            raise ValueError("All values in X should be positive")

        _, row_names, _, col_names = util.make_labels_and_names(X)

        if isinstance(X, pd.DataFrame):
            X = X.to_numpy()

        if self.copy:
            X = np.copy(X)

        # Compute the correspondence matrix which contains the relative frequencies
        X = X / np.sum(X)

        # Compute row and column masses
        self.row_masses_ = pd.Series(X.sum(axis=1), index=row_names)
        self.col_masses_ = pd.Series(X.sum(axis=0), index=col_names)

        # Compute standardised residuals
        r = self.row_masses_.to_numpy()
        c = self.col_masses_.to_numpy()
        S = sparse.diags(r ** -0.5) @ (X - np.outer(r, c)) @ sparse.diags(c ** -0.5)

        # Compute SVD on the standardised residuals
        self.U_, self.s_, self.V_ = svd.compute_svd(
            X=S,
            n_components=self.n_components,
            n_iter=self.n_iter,
            random_state=self.random_state,
            engine=self.engine
        )

        # Compute total inertia
        self.total_inertia_ = np.einsum('ij,ji->', S, S.T)

        return self

    def transform(self, X):
        """Computes the row principal coordinates of a dataset.

        Same as calling `row_coordinates`. In most cases you should be using the same
        dataset as you did when calling the `fit` method. You might however also want to included
        supplementary data.
        """
        utils.validation.check_is_fitted(self, 's_')
        if self.check_input:
            utils.check_array(X)
        return self.row_coordinates(X)

    @property
    def eigenvalues_(self):
        """The eigenvalues associated with each principal component."""
        utils.validation.check_is_fitted(self, 's_')
        return np.square(self.s_).tolist()

    @property
    def explained_inertia_(self):
        """The percentage of explained inertia per principal component."""
        utils.validation.check_is_fitted(self, 'total_inertia_')
        return [eig / self.total_inertia_ for eig in self.eigenvalues_]

    def row_coordinates(self, X):
        """The row principal coordinates."""
        utils.validation.check_is_fitted(self, 'V_')

        _, row_names, _, _ = util.make_labels_and_names(X)

        if isinstance(X, pd.SparseDataFrame):
            X = X.to_coo().astype(float)
        elif isinstance(X, pd.DataFrame):
            X = X.to_numpy()

        if self.copy:
            X = X.copy()

        # Normalise the rows so that they sum up to 1
        if isinstance(X, np.ndarray):
            X = X / X.sum(axis=1)[:, None]
        else:
            X = X / X.sum(axis=1)

        return pd.DataFrame(
            data=X @ sparse.diags(self.col_masses_.to_numpy() ** -0.5) @ self.V_.T,
            index=row_names
        )

    def column_coordinates(self, X):
        """The column principal coordinates."""
        utils.validation.check_is_fitted(self, 'V_')

        _, _, _, col_names = util.make_labels_and_names(X)

        if isinstance(X, pd.SparseDataFrame):
            X = X.to_coo()
        elif isinstance(X, pd.DataFrame):
            X = X.to_numpy()

        if self.copy:
            X = X.copy()

        # Transpose and make sure the rows sum up to 1
        if isinstance(X, np.ndarray):
            X = X.T / X.T.sum(axis=1)[:, None]
        else:
            X = X.T / X.T.sum(axis=1)

        return pd.DataFrame(
            data=X @ sparse.diags(self.row_masses_.to_numpy() ** -0.5) @ self.U_,
            index=col_names
        )

#     def plot_coordinates(self, X, ax=None, figsize=(6, 6), x_component=0, y_component=1,
#                                    show_row_labels=True, show_col_labels=True, **kwargs):
#         """Plot the principal coordinates."""

#         utils.validation.check_is_fitted(self, 's_')

#         if ax is None:
#             fig, ax = plt.subplots(figsize=figsize)

#         # Add style
#         ax = plot.stylize_axis(ax)

#         # Get labels and names
#         row_label, row_names, col_label, col_names = util.make_labels_and_names(X)

#         # Plot row principal coordinates
#         row_coords = self.row_coordinates(X)
#         ax.scatter(
#             row_coords[x_component],
#             row_coords[y_component],
#             **kwargs,
#             label=row_label
#         )

#         # Plot column principal coordinates
#         col_coords = self.column_coordinates(X)
#         ax.scatter(
#             col_coords[x_component],
#             col_coords[y_component],
#             **kwargs,
#             label=col_label
#         )

#         # Add row labels
#         if show_row_labels:
#             x = row_coords[x_component]
#             y = row_coords[y_component]
#             for xi, yi, label in zip(x, y, row_names):
#                 ax.annotate(label, (xi, yi))

#         # Add column labels
#         if show_col_labels:
#             x = col_coords[x_component]
#             y = col_coords[y_component]
#             for xi, yi, label in zip(x, y, col_names):
#                 ax.annotate(label, (xi, yi))

#         # Legend
#         ax.legend()

#         # Text
#         ax.set_title('Principal coordinates')
#         ei = self.explained_inertia_
#         ax.set_xlabel('Component {} ({:.2f}% inertia)'.format(x_component, 100 * ei[x_component]))
#         ax.set_ylabel('Component {} ({:.2f}% inertia)'.format(y_component, 100 * ei[y_component]))

#         return ax