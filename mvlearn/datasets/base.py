from os.path import dirname, join
import numpy as np


def load_UCImultifeature(select_labeled="all", shuffle=False,
                         random_state=None):
    r"""
    Load the UCI multiple features dataset [#1Data]_, taken from
    https://archive.ics.uci.edu/ml/datasets/Multiple+Features This data set
    consists of 6 views of handwritten digit images, with classes 0-9. The
    6 views are the following:

    1. 76 Fourier coefficients of the character shapes
    2. 216 profile correlations
    3. 64 Karhunen-Love coefficients
    4. 240 pixel averages of the images from 2x3 windows
    5. 47 Zernike moments
    6. 6 morphological features

    Each class contains 200 labeled examples.

    Parameters
    ----------
    select_labeled : optional, array-like, shape (n_features,) default (all)
        A list of the examples that the user wants by label. If not
        specified, all examples in the dataset are returned. Repeated labels
        are ignored.

    shuffle : bool, default=False
        If ``True``, returns each array with its rows and corresponding
        labels shuffled randomly according to ``random_state``.

    random_state : int, default=None
        Determines the order data is shuffled if ``shuffle=True``. Used so
        that data loaded is reproducible but shuffled.

    Returns
    -------
    data : list of np.ndarray, each of size (200*num_classes, n_features)
        List of length 6 with each element being the data for one of the
        views.

    labels : np.ndarray
        Array of labels for the digit

    References
    ----------
    .. [#1Data] M. van Breukelen, R.P.W. Duin, D.M.J. Tax, and J.E. den Hartog,
            Handwritten digit recognition by combined classifiers, Kybernetika,
            vol. 34, no. 4, 1998, 381-386

    Examples
    --------
    >>> from mvlearn.datasets import load_UCImultifeature
    >>> # Load full dataset with all 10 classes
    >>> full_data, full_labels = load_UCImultifeature()
    >>> print(len(full_data))
    6
    >>> print(full_data[0].shape)
    (2000, 76)
    >>> print(np.unique(full_labels))
    [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]
    >>> # Load only the examples labeled 0 or 1 (2 classes)
    >>> data, labels = load_UCImultifeature(select_labeled=[0,1])
    >>> print(len(data))
    6
    >>> print(data[0].shape)
    (400, 76)
    >>> print(np.unique(labels))
    [0. 1.]
    """

    if select_labeled == "all":
        select_labeled = range(10)

    if not shuffle:
        random_state = 1

    select_labeled = list(set(select_labeled))

    if len(select_labeled) < 1 or len(select_labeled) > 10:
        raise ValueError("If selecting examples by label, must select "
                         "at least 1 and no more than 10.")

    module_path = dirname(__file__)
    folder = "UCImultifeature"
    filenames = ["mfeat-fou.csv", "mfeat-fac.csv", "mfeat-kar.csv",
                 "mfeat-pix.csv", "mfeat-zer.csv", "mfeat-mor.csv"]

    data = []
    for filename in filenames:
        csv_file = join(module_path, folder, filename)
        datatemp = np.genfromtxt(csv_file, delimiter=',')
        data.append(datatemp[1:, :-1])
        labels = datatemp[1:, -1]

    selected_data = []
    for i in range(6):
        datatemp = np.zeros((200*len(select_labeled), data[i].shape[1]))
        if i == 0:
            selected_labels = np.zeros(200*len(select_labeled),)
        for j, label in enumerate(select_labeled):
            # user specified a bad label
            if label not in range(10):
                raise ValueError("Bad label: labels must be  in 0, 1, 2,.. 9")
            indices = np.nonzero(labels == label)
            datatemp[j * 200: (j+1) * 200, :] = data[i][indices, :]
            selected_labels[j*200:(j+1)*200] = labels[indices]

        np.random.seed(random_state)
        np.random.shuffle(datatemp)
        selected_data.append(datatemp)

    np.random.seed(random_state)
    np.random.shuffle(selected_labels)

    return selected_data, selected_labels
